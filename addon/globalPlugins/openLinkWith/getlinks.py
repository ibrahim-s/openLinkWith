# -*- coding: utf-8 -*-
#this module is aimed to get the links under selected text

import textInfos
import re
import api, ui
import addonHandler
addonHandler.initTranslation()

def find_urls (text):
	"""Find URLs in a text string.
	"""
	url_re = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ][^ \t\n\r\f\v]*")
	bad_chars = '\'\\.,[](){}:;"'
	return [s.strip(bad_chars) for s in url_re.findall(text)]

def isSelectedText():
	"""this function  specifies if a certain text is selected or not
	and if it is, returns text selected.
	"""

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
		# Translators: Displayed if there is no text selected.
		ui.message(_("No text selected"))
		return
	else:
		text= isSelectedText()
		links=find_urls(text)
		if links==[]:
			# Translators: Displayed if there is no links in selected text.
			ui.message(_("no links in selected text"))
			return
		else:
			return links