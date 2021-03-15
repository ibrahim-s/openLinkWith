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
	url_re = re.compile(r"(?:\w+://|www\.)[^ ,.?!#%=+][^ ][^ \t\n\r\f\v]*")
	bad_chars = '\'\\.,[](){}:;"'
	return [s.strip(bad_chars) for s in url_re.findall(text)]

def getClipText() -> str:
	try:
		return api.getClipData()
	except OSError:
		pass

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
	if not(isSelectedText() or getClipText()):
		# Translators: Display if no text is selected and there is no text in the clipboard.
		ui.message(_("You have not selected text and there is no text in the clipboard."))
		return
	else:
		text=str(getClipText()) +'\n'+ str(isSelectedText())
		links=find_urls(text)
		if links==[]:
			# Translators: Displayed if there is no links in selected text.
			ui.message(_("no links in selected text"))
			return
		else:
			return links