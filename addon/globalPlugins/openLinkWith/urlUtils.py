"""Utilities for matching URLs supported by Open Link With."""

from __future__ import annotations

import re
from urllib.parse import urlsplit


_URL_TERMINATOR_PATTERN = r'\s\x00-\x1f\x7f-\x9f<>"\\^`{|}'
_URL_PATTERN = re.compile(
	rf"(?:https?://|ftp://|www\.)"
	rf"[^,.?!#%=+{_URL_TERMINATOR_PATTERN}]"
	rf"[^{_URL_TERMINATOR_PATTERN}]*",
	re.IGNORECASE,
)
_INVALID_PERCENT_ESCAPE_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")
_UNCONDITIONAL_TRAILING_CHARACTERS = "'.,[(:;"
_CLOSING_TO_OPENING_DELIMITERS = {")": "(", "]": "["}
_TRIMMABLE_TRAILING_CHARACTERS = _UNCONDITIONAL_TRAILING_CHARACTERS + "".join(_CLOSING_TO_OPENING_DELIMITERS)


def _trimUrlEnd(url: str) -> str:
	"""Trim prose punctuation while preserving balanced URL delimiters."""
	suffixStart = len(url)
	while suffixStart and url[suffixStart - 1] in _TRIMMABLE_TRAILING_CHARACTERS:
		suffixStart -= 1

	delimiterBalance = {opening: 0 for opening in _CLOSING_TO_OPENING_DELIMITERS.values()}
	for index in range(suffixStart):
		character = url[index]
		if character in delimiterBalance:
			delimiterBalance[character] += 1
		elif character in _CLOSING_TO_OPENING_DELIMITERS:
			opening = _CLOSING_TO_OPENING_DELIMITERS[character]
			if delimiterBalance[opening]:
				delimiterBalance[opening] -= 1

	endIndex = suffixStart
	for index in range(suffixStart, len(url)):
		character = url[index]
		if character in delimiterBalance:
			delimiterBalance[character] += 1
		elif character in _CLOSING_TO_OPENING_DELIMITERS:
			opening = _CLOSING_TO_OPENING_DELIMITERS[character]
			if delimiterBalance[opening]:
				delimiterBalance[opening] -= 1
				endIndex = index + 1
	return url[:endIndex]


def findUrls(text: str) -> list[str]:
	"""Return unique supported URLs found in text, preserving their order."""
	urls: list[str] = []
	seenUrls: set[str] = set()
	for match in _URL_PATTERN.finditer(text):
		url = _trimUrlEnd(match.group(0))
		if url in seenUrls or not isSupportedUrl(url):
			continue
		seenUrls.add(url)
		urls.append(url)
	return urls


def isSupportedUrl(url: str) -> bool:
	"""Return whether the entire string is a supported URL."""
	if _URL_PATTERN.fullmatch(url) is None or _INVALID_PERCENT_ESCAPE_PATTERN.search(url):
		return False
	hasBareWwwPrefix = url[:4].casefold() == "www."
	urlToParse = f"http://{url}" if hasBareWwwPrefix else url
	try:
		parsedUrl = urlsplit(urlToParse)
		hostname = parsedUrl.hostname
		port = parsedUrl.port
	except ValueError:
		return False
	if not hostname or (hasBareWwwPrefix and hostname.rstrip(".").casefold() == "www"):
		return False
	return port is None or 0 <= port <= 65535
