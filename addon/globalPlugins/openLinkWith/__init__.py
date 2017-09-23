# -*- coding: utf-8 -*-
#This addon iextracts urls from selected text, put them in a list box in a dialog, and give you the opportunity to open them with various browsers on computer.
#This addon is under GNU General Public License gpl2.0.

import globalPluginHandler
import gui
from mydialog import MyDialog
from getlinks import getLinks
from getbrowsers import getBrowsers
import ui
import addonHandler
addonHandler.initTranslation()
DIALOG= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Open Link With")
	def script_opendialog(self, gesture):
		global DIALOG
		if DIALOG:
			#Translators: displayed if another instance of the dialog is present.
			ui.message(_("another instance of the dialog is openned, close it please"))
		else:
			list= getLinks()
			if list:
				browsers= getBrowsers()
				DIALOG= MyDialog(gui.mainFrame, list, browsers)
				DIALOG.postInit()
	#Translators: Message to be displayed in input help mode.
	script_opendialog.__doc__= _("Extract links in selected text, put them in list to open with")
