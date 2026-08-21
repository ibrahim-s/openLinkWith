# -*- coding: utf-8 -*-
#This addon extracts urls from selected text, last spoken or text in clipboard
#put them in a list box in a dialog, and give you the opportunity to open them with various browsers on computer.
#This addon is under GNU General Public License gpl2.0, Copyright (C) ibrahim hamadeh, Cary Rowen.
# See the file COPYING for more details.
# Hyper link menu feature, was inspired by Luke's contribution to access the link destination in NVDA core.

import globalPluginHandler
import webbrowser
import browseMode
import subprocess
import gui
import wx
from gui import guiHelper
import config
import globalVars
import api
import ui
import controlTypes
import queueHandler
import textInfos
from .mydialog import MyDialog, browsersGoPrivate
from .getlinks import LastSpoken, getLinksFromSelectedText, getLinksFromClipboard, getLinksFromLastSpoken
from .getbrowsers import getBrowsers
from .urlUtils import isSupportedUrl
from scriptHandler import script, getLastScriptRepeatCount
from logHandler import log

import addonHandler
addonHandler.initTranslation()

DIALOG= None

foundBrowsersNames= [browser for browser, path in getBrowsers()]
def getBrowserLabels():
	''' Get all browser labels, together with those available in private mode. '''
	result= []
	for browser in foundBrowsersNames:
		result.append(browser)
		if browser in browsersGoPrivate:
			result.append(browsersGoPrivate[browser][0])
	return result

def _getLinkInfoFromObject(obj):
	"""Return the nearest link object and its destination URL."""
	if obj is None:
		return
	try:
		linkData = obj.linkData
	except (AttributeError, NotImplementedError):
		linkData = None
	if linkData:
		return obj, linkData.destination
	if obj.role == controlTypes.role.Role.GRAPHIC:
		# Firefox exposes the URL on the graphic, while Chromium exposes it on the parent link.
		if obj.value:
			return obj, obj.value
		if obj.parent and obj.parent.role == controlTypes.role.Role.LINK:
			parentLink = obj.parent
			return parentLink, parentLink.value
	# Handle nested elements such as strong, em, or span inside a link.
	for _ in range(10):
		if obj is None:
			break
		if (
			obj.role == controlTypes.role.Role.LINK
			or controlTypes.state.State.LINKED in obj.states
		):
			return obj, obj.value
		obj = obj.parent


def getLinkInfo():
	"""Return the link object and destination URL at the caret or focus."""
	try:
		ti: textInfos.TextInfo = api.getCaretPosition()
	except RuntimeError:
		log.debugWarning("Unable to get the caret position.", exc_info=True)
		obj = api.getFocusObject()
	else:
		ti.expand(textInfos.UNIT_CHARACTER)
		obj = ti.NVDAObjectAtStart
	linkInfo = _getLinkInfoFromObject(obj)
	if linkInfo is None:
		# Translators: Tell user that the command has been run on something that is not a link
		ui.message(_("Not a link."))
		return
	_obj, linkDestination = linkInfo
	if not linkDestination:
		# Translators: Informs the user that the link has no destination
		ui.message(_("Link has no apparent destination"))
		return
	return linkInfo

class VirtualMenu():
	''' Helper class that deals with the virtual menu.
			This menu, when standing on a link, pops up to give you the option to open the link with other browsers on your machine.
	'''
	# If the menu already active or not.
	isActive= False
	# menuItems consist of browsers found, and those that may go private.
	menuItems= getBrowserLabels()
	index= 0
	# url for the link of interest.
	url= None

	@classmethod
	def showMenu(cls):
		#log.info(f'under show virtual menu ...')
		cls.index= 0
		cls.isActive= True
		# Translators: The title of virtual menu.
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Open link with menu"))
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, f"{cls.menuItems[cls.index]}")

	@classmethod
	def moveOnMenu(cls, key):
		if key== 'leftArrow' or key== 'rightArrow':
			return
		num= len(cls.menuItems)
		if key== 'downArrow':
			cls.index= (cls.index +1)%num
		elif key== 'upArrow':
			cls.index= (cls.index - 1)%num
		ui.message(f"{cls.menuItems[cls.index]}")

	@classmethod
	def clearMenu(cls, gbInstance, reportFocus= False):
		''' gbInstance is an instance of the GlobalPlugin class'''
		#log.info('clearing menu ...')
		# clearGestureBindings and bindGestures are attributes of a GlobalPlugin instance.
		gbInstance.clearGestureBindings()
		# __gestures is a private attributes, we use the syntax gbInstance._GlobalPlugin__gestures to access it.
		gbInstance.bindGestures(gbInstance._GlobalPlugin__gestures)
		cls.isActive= False
#if the virtual menu is closed by escape key, the navigator object does not announce itself
		# So we have to do that explicitly.
		if reportFocus:
			import speech
			speech.speakObject(cls.navigatorObject, reason=controlTypes.OutputReason.FOCUS)

	@classmethod
	def activateMenuItem(cls, gbInstance):
		''' Activating a menu item, and opening the link with a specific browser.
		gbInstance is a GlobalPlugin class instance.
		'''
		#log.info('Activating a menu item ...')
		try:
			# get the executable path of selected browser
			label= cls.menuItems[cls.index]
			basicBrowser= label.split('(')[0]if '(' in label else label
			exePath= [path for browser, path in getBrowsers() if browser== basicBrowser][0]
			if '(' in label :
				flag= browsersGoPrivate[basicBrowser][1]
				subprocess.Popen([exePath,flag, cls.url])
			else:
				subprocess.Popen(exePath+' '+cls.url)
		except Exception:
			# Translators: Message displayed if error happens in activating a menu item.
			message= _("Error in opening the link with {item} browser").format(item= cls.menuItems[cls.index])
			wx.CallAfter(gui.messageBox, message,
			# Translators: Title of message box
			_("Error Message"), style= wx.OK|wx.ICON_ERROR)
			log.info('Error activating menu item', exc_info= True)
		finally:
			cls.clearMenu(gbInstance)

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Category of addon in input gestures dialog.
	scriptCategory = _("Open Link With")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		LastSpoken.initialize()

		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OpenLinkWithPanel)

	def terminate(self):
		LastSpoken.terminate()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OpenLinkWithPanel)

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Display Open Link With dialog with extracted links from selected text.")
	)
	def script_displayLinksInSelectedText(self, gesture):
		global DIALOG
		if DIALOG:
			# Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
			return
		list_= getLinksFromSelectedText()
		if list_:
			if len(list_)==1 and config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]:
				webbrowser.open(list_[0], new=2)
				return
			browsers= getBrowsers()
			DIALOG= MyDialog(gui.mainFrame, list_, browsers)
			DIALOG.postInit()

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Display Open Link With dialog with extracted links from clipboard.")
	)
	def script_displayLinksInClipboardText(self, gesture):
		global DIALOG
		if DIALOG:
			# Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
			return
		list_= getLinksFromClipboard()
		if list_:
			if len(list_)==1 and config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]:
				webbrowser.open(list_[0], new=2)
				return
			browsers= getBrowsers()
			DIALOG= MyDialog(gui.mainFrame, list_, browsers)
			DIALOG.postInit()

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Display Open Link With dialog with extracted links from last spoken text.")
	)
	def script_displayLinksInLastSpokenText(self, gesture):
		global DIALOG
		if DIALOG:
			# Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
			return
		list_= getLinksFromLastSpoken()
		if list_:
			if len(list_)==1 and config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]:
				webbrowser.open(list_[0], new=2)
				return
			browsers= getBrowsers()
			DIALOG= MyDialog(gui.mainFrame, list_, browsers)
			DIALOG.postInit()

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Display a menu, if standing on a hyper link "
		"to give you the option to open the link with other browsers on  your machine."
		),
		gesture= "kb:alt+/"
	)
	def script_showVirtualMenu(self, gesture):
		#log.info('under script_showVirtualMenu...')
		linkInfo = getLinkInfo()
		if linkInfo is None:
			return
		obj, linkDestination = linkInfo
		# Some link destinations should not be opened with a browser.
		if not isSupportedUrl(linkDestination):
			# Translators: Message display if the link is not suited to open with the browser.
			message= _("The link {linkValue} is not suitable to open with the browser").format(linkValue= linkDestination)
			wx.CallAfter(gui.messageBox, message,
			# Translators: Title of message box.
			_("Information"), style= wx.OK|wx.ICON_INFORMATION)
			return
		if VirtualMenu.isActive:
			return
		# Bind gestures to work with virtual menu.
		for key in ('downArrow', 'upArrow', 'leftArrow', 'rightArrow', 'escape', 'enter'):
			self.bindGesture(f'kb:{key}', 'workOnVirtualMenu')
		VirtualMenu.navigatorObject= obj
		VirtualMenu.url= linkDestination
		VirtualMenu.showMenu()

	def script_workOnVirtualMenu(self, gesture):
		#log.info('under workOnVirtualMenu...')
		key= gesture.mainKeyName
		if key in ('upArrow', 'downArrow', 'leftArrow', 'rightArrow'):
			VirtualMenu.moveOnMenu(key)
		elif key== 'enter':
			VirtualMenu.activateMenuItem(self)
		elif key== 'escape':
			VirtualMenu.clearMenu(self, reportFocus= True)

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Announce address or link of a web page if pressed once, and copies it to clipboard when pressed twice."),
	)
	def script_getPageAddress(self, gesture):
		obj = api.getNavigatorObject().treeInterceptor
		if not isinstance(obj, browseMode.BrowseModeTreeInterceptor):
			gesture.send()
			return
		try:
			page_address = getattr(obj, 'documentURL', getattr(obj, 'documentConstantIdentifier', None))
		except Exception:
			log.error("Error getting page address", exc_info=True)
			ui.message(_("Unable to retrieve page address"))
			return
		#log.info(f'page_address: {page_address}')
		repeatCount = getLastScriptRepeatCount()
		if repeatCount == 0:
			ui.message(page_address)
		else:
			api.copyToClip(page_address, notify=True)

#default configuration for the addon
configspec={
	"closeDialogAfterActivatingALink": "boolean(default= False)",
	"openDirectlyIfThereIsOnlyOneLink": "boolean(default= False)"
}
config.conf.spec["openLinkWith"]= configspec

#make SettingsPanel class
class OpenLinkWithPanel(gui.settingsDialogs.SettingsPanel):
	# Translators: title of the dialog
	title= _("Open link with")

	def makeSettings(self, sizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: label of the check box 
		self.closeDialogCheckBox=wx.CheckBox(self,label=_("Close openLinkWith Dialog after activating a link"))
		self.closeDialogCheckBox.SetValue(config.conf["openLinkWith"]["closeDialogAfterActivatingALink"])
		settingsSizerHelper.addItem(self.closeDialogCheckBox)

		# Translators: label of the check box 
		self.openDirectlyCheckBox=wx.CheckBox(self,label=_("If only one link, open directly with default browser"))
		self.openDirectlyCheckBox.SetValue(config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"])
		settingsSizerHelper.addItem(self.openDirectlyCheckBox)

	def onSave(self):
		config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
		config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]= self.openDirectlyCheckBox.IsChecked() 
