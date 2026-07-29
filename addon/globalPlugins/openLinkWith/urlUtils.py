"""Utilities for matching URLs supported by Open Link With."""

from __future__ import annotations

import re
from socket import AF_INET6, inet_pton
import unicodedata
from urllib.parse import urlsplit


_URL_PREFIX_PATTERN = re.compile(r"(?:https?://|ftp://|www\.)", re.IGNORECASE)
_INVALID_INITIAL_URL_CHARACTERS = frozenset(",.?!#%=+")
_URL_TERMINATOR_CHARACTER_CLASS = (
	r'\s\x00-\x1f\x7f-\x9f<>"\\^`{|}'
	r"\u061c\u200b\u200e-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\ufeff\uff5c"
)
_URL_TERMINATOR_PATTERN = re.compile(rf"[{_URL_TERMINATOR_CHARACTER_CLASS}]")
_AUTHORITY_END_PATTERN = re.compile(rf"[/?#{_URL_TERMINATOR_CHARACTER_CLASS}]")
_INVALID_PERCENT_ESCAPE_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")
_IPV_FUTURE_PATTERN = re.compile(r"v[0-9A-Fa-f]+\.[-A-Za-z0-9._~!$&'()*+,;=:]+")
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


def _hasValidUrlStart(text: str, prefixEnd: int) -> bool:
	"""Return whether a supported prefix is followed by a possible URL character."""
	return (
		prefixEnd < len(text)
		and text[prefixEnd] not in _INVALID_INITIAL_URL_CHARACTERS
		and _URL_TERMINATOR_PATTERN.fullmatch(text[prefixEnd]) is None
	)


def _isAllowedHostnameCharacter(character: str) -> bool:
	"""Return whether a raw character can be part of a browser-facing hostname."""
	# cmark-gfm and linkify-it admit Unicode symbols as well as letters, marks, and numbers.
	return character in _HOSTNAME_PUNCTUATION_CHARACTERS or unicodedata.category(character)[0] in "LMNS"


def _isAllowedUserinfoCharacter(character: str) -> bool:
	"""Return whether a raw character can occur before an authority's final at sign."""
	if not character.isascii():
		return _URL_TERMINATOR_PATTERN.fullmatch(character) is None
	return character.isalnum() or character in _ASCII_USERINFO_CHARACTERS


def _isValidIpLiteral(hostname: str) -> bool:
	"""Return whether a bracketed hostname is a valid IPv6 or IPvFuture literal."""
	if _IPV_FUTURE_PATTERN.fullmatch(hostname) is not None:
		return True
	ipv6Address, zoneSeparator, zoneId = hostname.partition("%25")
	if "%" in ipv6Address or (zoneSeparator and (not zoneId or "%" in zoneId)):
		return False
	try:
		_ = inet_pton(AF_INET6, ipv6Address)
	except OSError:
		return False
	return True


def _findAuthorityEnd(text: str, urlStart: int, prefixEnd: int) -> int:
	"""Return the position where a URL authority ends."""
	if text[urlStart:prefixEnd].casefold() == "www.":
		hasPortSeparator = False
		for index in range(prefixEnd, len(text)):
			character = text[index]
			if character == ":" and not hasPortSeparator:
				hasPortSeparator = True
			elif _AUTHORITY_END_PATTERN.fullmatch(character) is not None or not _isAllowedHostnameCharacter(
				character
			):
				return index
		return len(text)
	match = _AUTHORITY_END_PATTERN.search(text, prefixEnd)
	return match.start() if match is not None else len(text)


def _findAuthorityBoundary(text: str, urlStart: int, prefixEnd: int, authorityEnd: int) -> int:
	"""Return the first prose boundary within a URL authority."""
	if text[urlStart:prefixEnd].casefold() == "www.":
		return authorityEnd
	authorityStart = prefixEnd
	userinfoEnd = text.rfind("@", authorityStart, authorityEnd)
	if userinfoEnd >= 0:
		for index in range(authorityStart, userinfoEnd):
			if not _isAllowedUserinfoCharacter(text[index]):
				return index
	hostnameStart = userinfoEnd + 1 if userinfoEnd >= 0 else authorityStart
	if hostnameStart >= authorityEnd:
		return authorityEnd

	if text[hostnameStart] == "[":
		closingBracket = text.find("]", hostnameStart + 1, authorityEnd)
		if closingBracket < 0:
			return authorityEnd
		hostnameEnd = closingBracket + 1
	else:
		portSeparator = text.find(":", hostnameStart, authorityEnd)
		hostnameEnd = portSeparator if portSeparator >= 0 else authorityEnd
		for index in range(hostnameStart, hostnameEnd):
			if not _isAllowedHostnameCharacter(text[index]):
				return index

	if hostnameEnd >= authorityEnd:
		return authorityEnd
	portStart = hostnameEnd + 1 if text[hostnameEnd] == ":" else hostnameEnd
	for index in range(portStart, authorityEnd):
		if not _isAllowedHostnameCharacter(text[index]):
			return index
	return authorityEnd


def _findUrlCandidateEnd(text: str, urlStart: int, prefixEnd: int) -> int:
	"""Return the end of one URL candidate without scanning later candidates."""
	authorityEnd = _findAuthorityEnd(text, urlStart, prefixEnd)
	authorityBoundary = _findAuthorityBoundary(text, urlStart, prefixEnd, authorityEnd)
	if authorityBoundary < authorityEnd:
		return authorityBoundary
	if authorityEnd >= len(text) or text[authorityEnd] not in "/?#":
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

	delimiterBalance = dict.fromkeys(_OPENING_TO_CLOSING_DELIMITERS, 0)
	endIndex = suffixStart
	for index, character in enumerate(url):
		if character in delimiterBalance:
			delimiterBalance[character] += 1
		elif character in _CLOSING_TO_OPENING_DELIMITERS:
			opening = _CLOSING_TO_OPENING_DELIMITERS[character]
			if delimiterBalance[opening]:
				delimiterBalance[opening] -= 1
				if index >= suffixStart:
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
	if prefixMatch is None or not _hasValidUrlStart(url, prefixMatch.end()):
		return False
	authorityEnd = _findAuthorityEnd(url, 0, prefixMatch.end())
	if (
		_URL_TERMINATOR_PATTERN.search(url) is not None
		or _INVALID_PERCENT_ESCAPE_PATTERN.search(url)
		or (authorityEnd < len(url) and url[authorityEnd] not in "/?#")
		or _findAuthorityBoundary(url, 0, prefixMatch.end(), authorityEnd) != authorityEnd
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
	hostAndPort = parsedUrl.netloc.rsplit("@", 1)[-1]
	if hostAndPort.startswith("[") and not _isValidIpLiteral(hostAndPort[1:].partition("]")[0]):
		return False
	return port is None or 0 <= port <= 65535
