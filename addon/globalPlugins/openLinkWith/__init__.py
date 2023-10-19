# -*- coding: utf-8 -*-
#This addon extracts urls from selected text, last spoken or text in clipboard
#put them in a list box in a dialog, and give you the opportunity to open them with various browsers on computer.
#This addon is under GNU General Public License gpl2.0, Copyright (C) ibrahim hamadeh, Cary Rowen.
# See the file COPYING for more details.
# Hyper link menu feature, was inspired by Luke's contribution to access the link destination in NVDA core.

import globalPluginHandler
import webbrowser
import subprocess
import gui, wx
from gui import guiHelper
import config
import globalVars
import api
import ui
import controlTypes
import queueHandler
from .mydialog import MyDialog
from .getlinks import LastSpoken, getLinksFromSelectedText, getLinksFromClipboard, getLinksFromLastSpoken
from .getbrowsers import getBrowsers
from scriptHandler import script
from logHandler import log

import addonHandler
addonHandler.initTranslation()

DIALOG= None

class VirtualMenu():
	''' Helper class that deals with the virtual menu.
			This menu, when standing on a link, pops up to give you the option to open the link with other browsers on your machine.
	'''
	# If the menu already active or not.
	isActive= False
	menuItems= [browser for browser, path in getBrowsers()]
	index= 0
	# url for the link of interest.
	url= None

	@classmethod
	def showMenu(cls):
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
			exePath= getBrowsers()[cls.index][1]
			#log.info(f'url: {cls.url}')
			subprocess.Popen(exePath+' '+cls.url)
		except:
			# Translators: Message displayed if error happens in activating a menu item.
			message= _("Error in opening the link with {item} browser").format(item= getBrowsers()[cls.index][0])
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
		LastSpoken._patch()

		if hasattr(gui.settingsDialogs, 'SettingsPanel'):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OpenLinkWithSettings)
		else:
			self.prefmenu= gui.mainFrame.sysTrayIcon.preferencesMenu
			self.addonmenu= self.prefmenu.Append(wx.ID_ANY,
			# Translators: label of openLinkWith setting menu in preferences menu
			_("OpenLinkWith..."),
			"Opens setting dialog"
			)
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onOpenSettingDialog, self.addonmenu)

	def onOpenSettingDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(OpenLinkWithSettings)

	def terminate(self):
		LastSpoken.terminate()
		if hasattr(gui.settingsDialogs, 'SettingsPanel'):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OpenLinkWithSettings)
		else:
			try:
				self.prefmenu.RemoveItem(self.addonmenu)
			except :
				pass

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
				webbrowser.open(list_[0])
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
				webbrowser.open(list_[0])
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
				webbrowser.open(list_[0])
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
		obj = api.getNavigatorObject()
		if not (
			obj.role == controlTypes.role.Role.LINK  # If it's a link, or
			or controlTypes.state.State.LINKED in obj.states  # if it isn't a link but contains one
		):
			# Translators: Tell user that the command has been run on something that is not a link
			ui.message(_("Not a link."))
			return
		# It is a link, but may be it's value is an email or other thing that shouldn't be opened with a browser.
		import re
		if not re.match(r'https?://|ftp://|www.', obj.value):
			# Translators: Message display if the link is not suited to open with the browser.
			message= _("The link {linkValue} is not suitable to open with the browser").format(linkValue= obj.value)
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
		VirtualMenu.url= obj.value
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

#default configuration of settings dialog or panel for the addon
configspec={
	"closeDialogAfterActivatingALink": "boolean(default= False)",
	"openDirectlyIfThereIsOnlyOneLink": "boolean(default= False)"
}
config.conf.spec["openLinkWith"]= configspec

#make either SettingsPanel or SettingsDialog class
parentClass= gui.settingsDialogs.SettingsPanel if hasattr(gui.settingsDialogs, 'SettingsPanel') else gui.settingsDialogs.SettingsDialog
class OpenLinkWithSettings(parentClass):
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

	if hasattr(parentClass, 'onSave'):
		def onSave(self):
			config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
			config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]= self.openDirectlyCheckBox.IsChecked() 

	else:
		def onOk(self, evt):
			config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
			config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]= self.openDirectlyCheckBox.IsChecked() 
			super(OpenLinkWithSettings, self).onOk(evt)

		def postInit(self):
			self.closeDialogCheckBox.SetFocus()
