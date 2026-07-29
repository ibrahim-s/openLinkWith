"""Utilities for matching URLs supported by Open Link With."""

import re


_BAD_URL_END_CHARACTERS = "'\\.,[](){}:;\""
_URL_PATTERN = re.compile(
	r'(?:https?://|ftp://|www\.)[^ ,.?!#%=+<>"\\][^\s<>"\\]*',
	re.IGNORECASE,
)


def findUrls(text: str) -> list[str]:
	"""Return unique supported URLs found in text, preserving their order."""
	return list(
		dict.fromkeys(match.group(0).strip(_BAD_URL_END_CHARACTERS) for match in _URL_PATTERN.finditer(text))
	)


def isSupportedUrl(url: str) -> bool:
	"""Return whether the entire string is a supported URL."""
	return _URL_PATTERN.fullmatch(url) is not None


def _runConfidenceCheck() -> None:
	"""Run a small confidence check for URL matching."""
	assert findUrls("wwwXexample.com") == []
	assert findUrls("http://a\nnext") == ["http://a"]
	assert findUrls("HTML https://example.com</a>") == ["https://example.com"]
	assert findUrls("HTTPS://example.com WWW.example.com") == [
		"HTTPS://example.com",
		"WWW.example.com",
	]
	assert findUrls("https://example.com?") == ["https://example.com?"]
	unicodeUrl = "https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84"
	assert findUrls(unicodeUrl) == [unicodeUrl]
	assert isSupportedUrl("https://example.com")
	assert not isSupportedUrl("http://")
	assert not isSupportedUrl("https://example.com</a>")


if __name__ == "__main__":
	_runConfidenceCheck()
