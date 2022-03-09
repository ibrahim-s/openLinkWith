# -*- coding: utf-8 -*-
#This addon extracts urls from selected text or text in clipboard
#put them in a list box in a dialog, and give you the opportunity to open them with various browsers on computer.
#This addon is under GNU General Public License gpl2.0, Copyright (C) ibrahim hamadeh.
# See the file COPYING for more details.

import globalPluginHandler
import gui, wx
from gui import guiHelper
import config
from .mydialog import MyDialog
from .getlinks import getLinksFromSelectedText, getLinksFromClipboard
from .getbrowsers import getBrowsers
import ui
from scriptHandler import script
from logHandler import log
import addonHandler
addonHandler.initTranslation()

DIALOG= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Category of addon in input gestures dialog.
	scriptCategory = _("Open Link With")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

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
		if hasattr(gui, 'SettingsPanel'):
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
		else:
			list_= getLinksFromSelectedText()
			if list_:
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
				browsers= getBrowsers()
				DIALOG= MyDialog(gui.mainFrame, list_, browsers)
				DIALOG.postInit()

#default configuration of settings dialog or panel for the addon
configspec={
	"closeDialogAfterActivatingALink": "boolean(default= False)"
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

	if hasattr(parentClass, 'onSave'):
		def onSave(self):
			config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 

	else:
		def onOk(self, evt):
			config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
			super(OpenLinkWithSettings, self).onOk(evt)

		def postInit(self):
			self.closeDialogCheckBox.SetFocus()
