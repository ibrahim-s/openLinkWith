# -*- coding: utf-8 -*-
#This addon extracts urls from selected text or text in clipboard
#put them in a list box in a dialog, and give you the opportunity to open them with various browsers on computer.
#This addon is under GNU General Public License gpl2.0, Copyright (C) ibrahim hamadeh.
# See the file COPYING for more details.

import globalPluginHandler
import webbrowser
import gui, wx
from gui import guiHelper
import config
import globalVars
import ui
from .mydialog import MyDialog
from .getLastSpoken import LastSpoken
from .getlinks import getLinksFromSelectedText, getLinksFromClipboard, getLinksFromLastSpoken
from .getbrowsers import getBrowsers
from scriptHandler import script
from logHandler import log

import addonHandler
addonHandler.initTranslation()

DIALOG= None

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

		if hasattr(gui, 'SettingsPanel'):
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
		if hasattr(gui, 'SettingsPanel'):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OpenLinkWithSettings)
		else:
			try:
				self.prefmenu.RemoveItem(self.addonmenu)
			except :
				pass

	@script(
		# Translators: Message to be displayed in input help mode.
		description= _("Display Open Link With dialog with extracted links from last spoken text.")
	)
	def script_displayLinksInLastSpokenText(self, gesture):
		global DIALOG
		if DIALOG:
			# Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
		else:
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
		description= _("Display Open Link With dialog with extracted links from selected text.")
	)
	def script_displayLinksInSelectedText(self, gesture):
		global DIALOG
		if DIALOG:
			# Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
		else:
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
		else:
			list_= getLinksFromClipboard()
			if list_:
				if len(list_)==1 and config.conf["openLinkWith"]["openDirectlyIfThereIsOnlyOneLink"]:
					webbrowser.open(list_[0])
					return
				browsers= getBrowsers()
				DIALOG= MyDialog(gui.mainFrame, list_, browsers)
				DIALOG.postInit()

#default configuration of settings dialog or panel for the addon
configspec={
	"closeDialogAfterActivatingALink": "boolean(default= False)",
	"openDirectlyIfThereIsOnlyOneLink": "boolean(default= True)"
}
config.conf.spec["openLinkWith"]= configspec

parentClass= gui.SettingsPanel if hasattr(gui, 'SettingsPanel') else gui.SettingsDialog
#make either SettingsPanel or SettingsDialog class
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
		self.openDirectlyCheckBox=wx.CheckBox(self,label=_("Open directly if there is only one link"))
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
