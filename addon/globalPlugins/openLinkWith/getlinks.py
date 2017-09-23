# -*- coding: utf-8 -*-
#this module is aimed to get the links under selected text

import textInfos
import urlfinder
import api, ui
import addonHandler
addonHandler.initTranslation()

#the function that specifies if a certain text is selected or not
#and if it is, returns text selected
#this piece of code really is taken from a previous addon, thanks to the hands behind it.
def isSelectedText():
	obj=api.getFocusObject()
	treeInterceptor=obj.treeInterceptor
	if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
		obj=treeInterceptor
	try:
		info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError):
		info=None
	if not info or info.isCollapsed:
		return False
	else:
		return info.text

def getLinks():
	"""This function returns a list of links if present under selected text.
	"""
	if not isSelectedText():
		#Translators: Displayed if there is no text selected.
		ui.message(_("No text selected"))
		return
	else:
		text= isSelectedText()
		links=urlfinder.find_urls(text)
		if links==[]:
			#Translators: Displayed if there is no links in selected text.
			ui.message(_("no links in selected text"))
			return
		else:
			return links