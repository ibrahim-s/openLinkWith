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
		cls.lastSpokenText = None

	@classmethod
	def getText(cls):
		"""Return the most recent non-empty speech text, if available."""
		return cls.lastSpokenText

	@classmethod
	def _onSpeech(cls, speechSequence):
		"""Store the text from a speech sequence."""
		text = CHUNK_SEPARATOR.join(item for item in speechSequence if isinstance(item, str)).strip()
		if text:
			cls.lastSpokenText = text


def getClipText() -> str:
	"""Return the text currently stored on the Windows clipboard."""
	try:
		return api.getClipData()
	except OSError:
		return ""


def isSelectedText():
	"""Return selected text from the focus object, or None if unavailable."""
	try:
		obj = api.getFocusObject()
		if obj is None:
			return None
		treeInterceptor = getattr(obj, "treeInterceptor", None)
		if (
			treeInterceptor is not None
			and hasattr(treeInterceptor, "TextInfo")
			and not getattr(treeInterceptor, "passThrough", False)
		):
			obj = treeInterceptor
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		if not info or info.isCollapsed:
			return None
		return info.text
	except (AttributeError, RuntimeError, NotImplementedError):
		return None

def getLinksFromSelectedText():
	"""This function returns a list of links if present under selected text."""
	text = isSelectedText()
	if not text:
		# Translators: Displayed if there is no text selected.
		ui.message(_("No text selected"))
		return
	links = findUrls(text)
	if not links:
		# Translators: Displayed if there is no links in selected text.
		ui.message(_("no links in selected text"))
		return
	return links

def getLinksFromClipboard():
	"""This function returns a list of links if present in clipboard text."""
	text = getClipText()
	if not text:
		# Translators: Message displayed when there is no text in clipboard.
		ui.message(_("No text in clipboard."))
		return
	links = findUrls(text)
	if not links:
		# Translators: Message displayed when there is no links in clipboard text.
		ui.message(_("No links in clipboard text."))
		return
	return links

def getLinksFromLastSpoken():
	"""This function returns a list of links if present in last spoken text."""
	text = LastSpoken.getText()
	if not text:
		# Translators: Message displayed when there is no text in LastSpoken
		ui.message(_("No text."))
		return
	links = findUrls(text)
	if not links:
		# Translators: Message displayed when there is no links in last spoken text.
		ui.message(_("No links in last spoken text."))
		return
	return links


def getLinksFromContext():
	"""Return links from selected text, last spoken text, or clipboard, in that order."""
	for getText in (isSelectedText, LastSpoken.getText, getClipText):
		try:
			text = getText()
		except (OSError, RuntimeError, NotImplementedError):
			continue
		if isinstance(text, str) and text:
			links = findUrls(text)
			if links:
				return links
