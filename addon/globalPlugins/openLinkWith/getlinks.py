import textInfos
import api
import ui
from speech.extensions import pre_speech
from speech.speech import CHUNK_SEPARATOR

from .urlUtils import findUrls

import addonHandler
addonHandler.initTranslation()

class LastSpoken:
	"""Track the most recent non-empty speech text."""

	lastSpokenText = None

	@classmethod
	def initialize(cls):
		"""Register the speech extension point handler."""
		pre_speech.register(cls._onSpeech)

	@classmethod
	def terminate(cls):
		"""Unregister the speech extension point handler."""
		pre_speech.unregister(cls._onSpeech)

	@classmethod
	def _onSpeech(cls, speechSequence):
		"""Store the text from a speech sequence."""
		text = CHUNK_SEPARATOR.join(item for item in speechSequence if isinstance(item, str)).strip()
		if text:
			cls.lastSpokenText = text


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

def getLinksFromSelectedText():
	"""This function returns a list of links if present under selected text."""
	if not isSelectedText():
		# Translators: Displayed if there is no text selected.
		ui.message(_("No text selected"))
		return
	else:
		text= isSelectedText()
		links=findUrls(text)
		if not links:
			# Translators: Displayed if there is no links in selected text.
			ui.message(_("no links in selected text"))
			return
		else:
			return links

def getLinksFromClipboard():
	"""This function returns a list of links if present in clipboard text."""
	text= getClipText()
	if not text:
		# Translators: Message displayed when there is no text in clipboard.
		ui.message(_("No text in clipboard."))
		return
	else:
		links=findUrls(text)
		if not links:
			# Translators: Message displayed when there is no links in clipboard text.
			ui.message(_("No links in clipboard text."))
			return
		else:
			return links

def getLinksFromLastSpoken():
	"""This function returns a list of links if present in last spoken text."""
	text= LastSpoken.lastSpokenText
	if not text:
		# Translators: Message displayed when there is no text in LastSpoken
		ui.message(_("No text."))
		return
	else:
		links=findUrls(text)
		if not links:
			# Translators: Message displayed when there is no links in last spoken text.
			ui.message(_("No links in last spoken text."))
			return
		else:
			return links
