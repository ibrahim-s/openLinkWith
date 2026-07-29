"""Utilities for matching URLs supported by Open Link With."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit


_URL_PREFIX_PATTERN = re.compile(r"(?:https?://|ftp://|www\.)", re.IGNORECASE)
_INVALID_INITIAL_URL_CHARACTERS = frozenset(",.?!#%=+")
_URL_TERMINATOR_PATTERN = re.compile(
	r'[\s\x00-\x1f\x7f-\x9f<>"\\^`{|}'
	r"\u061c\u200b\u200e-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\ufeff\uff5c]"
)
_INVALID_PERCENT_ESCAPE_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")
_HOSTNAME_PUNCTUATION_CHARACTERS = frozenset(
	".-_%\u00b7\u0375\u05f3\u05f4\u200c\u200d\u3002\u30fb\uff0d\uff0e\uff3f\uff61"
)
_ASCII_USERINFO_CHARACTERS = frozenset("-._~%!$&'()*+,;=:@")
_UNCONDITIONAL_TRAILING_CHARACTERS = (
	"'.,:;"
	"\u055d\u055e\u0589\u05c3\u060c\u061b\u061f\u06d4"
	"\u0964\u0965\u0f0d\u0f0e\u104a\u104b\u1362\u1367"
	"\u3001\u3002\uff01\uff0c\uff0e\uff1a\uff1b\uff1f\uff61"
)
_CLOSING_TO_OPENING_DELIMITERS = {
	")": "(",
	"]": "[",
	"\u00bb": "\u00ab",
	"\u2019": "\u2018",
	"\u201d": "\u201c",
	"\u203a": "\u2039",
	"\u3009": "\u3008",
	"\u300b": "\u300a",
	"\u300d": "\u300c",
	"\u300f": "\u300e",
	"\u3011": "\u3010",
	"\u3015": "\u3014",
	"\u3017": "\u3016",
	"\u3019": "\u3018",
	"\u301b": "\u301a",
	"\uff63": "\uff62",
	"\uff09": "\uff08",
	"\uff3d": "\uff3b",
	"\uff5d": "\uff5b",
}
_OPENING_TO_CLOSING_DELIMITERS = {
	opening: closing for closing, opening in _CLOSING_TO_OPENING_DELIMITERS.items()
}
_TRIMMABLE_TRAILING_CHARACTERS = (
	_UNCONDITIONAL_TRAILING_CHARACTERS
	+ "".join(_CLOSING_TO_OPENING_DELIMITERS)
	+ "".join(_CLOSING_TO_OPENING_DELIMITERS.values())
)


def _isUrlTerminator(character: str) -> bool:
	"""Return whether a character definitely ends a raw URL candidate."""
	return _URL_TERMINATOR_PATTERN.fullmatch(character) is not None


def _hasValidUrlStart(text: str, prefixEnd: int) -> bool:
	"""Return whether a supported prefix is followed by a possible URL character."""
	return (
		prefixEnd < len(text)
		and text[prefixEnd] not in _INVALID_INITIAL_URL_CHARACTERS
		and not _isUrlTerminator(text[prefixEnd])
	)


def _isAllowedHostnameCharacter(character: str) -> bool:
	"""Return whether a raw character can be part of a browser-facing hostname."""
	if character in _HOSTNAME_PUNCTUATION_CHARACTERS:
		return True
	# cmark-gfm and linkify-it admit Unicode symbols as well as letters, marks, and numbers.
	return unicodedata.category(character)[0] in "LMNS"


def _isAllowedUserinfoCharacter(character: str) -> bool:
	"""Return whether a raw character can occur before an authority's final at sign."""
	if not character.isascii():
		return not _isUrlTerminator(character)
	return character.isalnum() or character in _ASCII_USERINFO_CHARACTERS


def _truncateAtAuthorityBoundary(url: str) -> str:
	"""Stop a URL candidate at prose punctuation in its hostname or port."""
	authorityStart = 0 if url[:4].casefold() == "www." else url.find("://") + 3
	authorityEnd = len(url)
	for separator in "/?#":
		separatorIndex = url.find(separator, authorityStart)
		if separatorIndex >= 0:
			authorityEnd = min(authorityEnd, separatorIndex)
	userinfoEnd = url.rfind("@", authorityStart, authorityEnd)
	if userinfoEnd >= 0:
		for index in range(authorityStart, userinfoEnd):
			if not _isAllowedUserinfoCharacter(url[index]):
				return url[:index]
	hostnameStart = userinfoEnd + 1 if userinfoEnd >= 0 else authorityStart
	if hostnameStart >= authorityEnd:
		return url

	if url[hostnameStart] == "[":
		closingBracket = url.find("]", hostnameStart + 1, authorityEnd)
		if closingBracket < 0:
			return url
		hostnameEnd = closingBracket + 1
	else:
		portSeparator = url.find(":", hostnameStart, authorityEnd)
		hostnameEnd = portSeparator if portSeparator >= 0 else authorityEnd
		for index in range(hostnameStart, hostnameEnd):
			if not _isAllowedHostnameCharacter(url[index]):
				return url[:index]

	if hostnameEnd >= authorityEnd:
		return url
	portStart = hostnameEnd + 1 if url[hostnameEnd] == ":" else hostnameEnd
	for index in range(portStart, authorityEnd):
		if not _isAllowedHostnameCharacter(url[index]):
			return url[:index]
	return url


def _findUrlCandidateEnd(text: str, urlStart: int, prefixEnd: int) -> int:
	"""Return the end of one URL candidate without scanning later candidates."""
	authorityEnd = len(text)
	for separator in "/?#":
		separatorIndex = text.find(separator, prefixEnd)
		if separatorIndex >= 0:
			authorityEnd = min(authorityEnd, separatorIndex)
	terminatorMatch = _URL_TERMINATOR_PATTERN.search(text, prefixEnd, authorityEnd)
	if terminatorMatch is not None:
		authorityEnd = terminatorMatch.start()

	authorityCandidate = text[urlStart:authorityEnd]
	truncatedAuthority = _truncateAtAuthorityBoundary(authorityCandidate)
	if len(truncatedAuthority) < len(authorityCandidate):
		return urlStart + len(truncatedAuthority)
	if authorityEnd >= len(text) or _isUrlTerminator(text[authorityEnd]):
		return authorityEnd

	precedingCharacter = text[urlStart - 1] if urlStart else ""
	closing = _OPENING_TO_CLOSING_DELIMITERS.get(precedingCharacter)
	if precedingCharacter == "'":
		closingIndex = text.find("'", authorityEnd)
		searchEnd = closingIndex if closingIndex >= 0 else len(text)
		terminatorMatch = _URL_TERMINATOR_PATTERN.search(text, authorityEnd, searchEnd)
		return terminatorMatch.start() if terminatorMatch is not None else searchEnd
	if closing is None:
		terminatorMatch = _URL_TERMINATOR_PATTERN.search(text, authorityEnd)
		return terminatorMatch.start() if terminatorMatch is not None else len(text)

	delimiterDepth = 1
	searchStart = authorityEnd
	while searchStart < len(text):
		nextOpening = text.find(precedingCharacter, searchStart)
		nextClosing = text.find(closing, searchStart)
		nextDelimiter = min(
			(index for index in (nextOpening, nextClosing) if index >= 0),
			default=len(text),
		)
		terminatorMatch = _URL_TERMINATOR_PATTERN.search(text, searchStart, nextDelimiter)
		if terminatorMatch is not None:
			return terminatorMatch.start()
		if nextDelimiter >= len(text):
			return len(text)
		if nextDelimiter == nextOpening:
			delimiterDepth += 1
		else:
			delimiterDepth -= 1
			if delimiterDepth == 0:
				return nextDelimiter
		searchStart = nextDelimiter + 1
	return len(text)


def _trimUrlEnd(url: str) -> str:
	"""Trim prose punctuation while preserving balanced URL delimiters."""
	suffixStart = len(url)
	while suffixStart and url[suffixStart - 1] in _TRIMMABLE_TRAILING_CHARACTERS:
		suffixStart -= 1
	if suffixStart == len(url):
		return url

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
	searchStart = 0
	while True:
		prefixMatch = _URL_PREFIX_PATTERN.search(text, searchStart)
		if prefixMatch is None:
			break
		if not _hasValidUrlStart(text, prefixMatch.end()):
			searchStart = prefixMatch.end()
			continue
		candidateEnd = _findUrlCandidateEnd(text, prefixMatch.start(), prefixMatch.end())
		url = _trimUrlEnd(text[prefixMatch.start() : candidateEnd])
		searchStart = max(candidateEnd, prefixMatch.end())
		if url in seenUrls or not isSupportedUrl(url):
			continue
		seenUrls.add(url)
		urls.append(url)
	return urls


def isSupportedUrl(url: str) -> bool:
	"""Return whether the entire string is a supported URL."""
	prefixMatch = _URL_PREFIX_PATTERN.match(url)
	if (
		prefixMatch is None
		or not _hasValidUrlStart(url, prefixMatch.end())
		or _URL_TERMINATOR_PATTERN.search(url) is not None
		or _INVALID_PERCENT_ESCAPE_PATTERN.search(url)
		or _truncateAtAuthorityBoundary(url) != url
	):
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
