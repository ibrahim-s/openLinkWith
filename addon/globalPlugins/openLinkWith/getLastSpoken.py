import speech
import speechViewer
import versionInfo

class LastSpoken:
	''' Helper class that contains the code, to get last spoken text.'''
	BUILD_YEAR = getattr(versionInfo, 'version_year', 2021)
	lastSpokenText=None

	@classmethod
	def _patch(cls):
		if cls.BUILD_YEAR >= 2021:
			cls.oldSpeak = speech.speech.speak
			speech.speech.speak = cls.mySpeak
		else:
			cls.oldSpeak = speech.speak
			speech.speak = cls.mySpeak

	@classmethod
	def terminate(cls):
		if cls.BUILD_YEAR >= 2021:
			speech.speech.speak = cls.oldSpeak
		else:
			speech.speak = cls.oldSpeak

	@classmethod
	def mySpeak(cls, sequence, *args, **kwargs):
		cls.oldSpeak(sequence, *args, **kwargs)
		text = speechViewer.SPEECH_ITEM_SEPARATOR.join([x for x in sequence if isinstance(x, str)])
		if text.strip():
			cls.lastSpokenText=text.strip()
