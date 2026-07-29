"""Unit tests for Open Link With URL matching utilities."""

import ast
from collections.abc import Callable
from pathlib import Path
import runpy
from typing import cast
import unittest


_URL_UTILS_PATH = Path(__file__).parents[2] / "addon" / "globalPlugins" / "openLinkWith" / "urlUtils.py"
_URL_UTILS_NAMESPACE = runpy.run_path(str(_URL_UTILS_PATH))
_findUrls = cast(Callable[[str], list[str]], _URL_UTILS_NAMESPACE["findUrls"])
_isSupportedUrl = cast(Callable[[str], bool], _URL_UTILS_NAMESPACE["isSupportedUrl"])


class FindUrlsTests(unittest.TestCase):
	"""Tests for extracting supported URLs from text."""

	def testDefiniteTerminators(self) -> None:
		"""Stop at characters which cannot occur raw in a URI or IRI."""
		cases = (
			("http://\nnext", []),
			("http://\tnext", []),
			('http://a\nnext"', ["http://a"]),
			("https://example.com\x00suffix", ["https://example.com"]),
			("https://example.com^suffix", ["https://example.com"]),
			("https://example.com`suffix", ["https://example.com"]),
			("https://example.com{suffix", ["https://example.com"]),
			("https://example.com|suffix", ["https://example.com"]),
			("https://example.com}suffix", ["https://example.com"]),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual(expected, _findUrls(text))

	def testAllControlAndForbiddenRawCharactersTerminateCandidates(self) -> None:
		"""Treat every C0/C1 control and forbidden raw ASCII character as a boundary."""
		terminators = [chr(value) for value in range(0x00, 0x20)]
		terminators.extend(chr(value) for value in range(0x7F, 0xA0))
		terminators.extend('<>"\\^`{|}')
		for character in terminators:
			text = f"https://example.com{character}suffix"
			with self.subTest(codePoint=f"U+{ord(character):04X}"):
				self.assertEqual(["https://example.com"], _findUrls(text))
				self.assertFalse(_isSupportedUrl(text))

	def testUnicodeWhitespaceTerminatesCandidates(self) -> None:
		"""Stop at representative non-ASCII whitespace characters."""
		for character in ("\u00a0", "\u1680", "\u2000", "\u2028", "\u2029", "\u202f", "\u205f", "\u3000"):
			with self.subTest(codePoint=f"U+{ord(character):04X}"):
				self.assertEqual(
					["https://example.com"],
					_findUrls(f"https://example.com{character}suffix"),
				)

	def testBalancedDelimiters(self) -> None:
		"""Preserve balanced URL delimiters and trim surrounding prose delimiters."""
		cases = (
			("http://[::1]", ["http://[::1]"]),
			(
				"https://en.wikipedia.org/wiki/Function_(mathematics)",
				["https://en.wikipedia.org/wiki/Function_(mathematics)"],
			),
			("(https://example.com)", ["https://example.com"]),
			("(https://example.com/a(b))", ["https://example.com/a(b)"]),
			("https://example.com/a(b)))", ["https://example.com/a(b)"]),
			("[http://[::1]]", ["http://[::1]"]),
			("https://example.com/][]", ["https://example.com/][]"]),
			("https://example.com/a((b))", ["https://example.com/a((b))"]),
			("https://example.com/a[b[0]]", ["https://example.com/a[b[0]]"]),
			("[http://[::1]/a[0]]", ["http://[::1]/a[0]"]),
			("(https://example.com/a(b)).", ["https://example.com/a(b)"]),
			("https://example.com/a[0]]);", ["https://example.com/a[0]"]),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual(expected, _findUrls(text))

	def testTrimsOnlyTrailingProsePunctuation(self) -> None:
		"""Trim established prose suffixes without removing punctuation inside URLs."""
		cases = (
			("https://example.com.", ["https://example.com"]),
			("https://example.com,;'", ["https://example.com"]),
			("https://example.com:([", ["https://example.com"]),
			("https://example.com/a,b", ["https://example.com/a,b"]),
			("https://example.com/a;b", ["https://example.com/a;b"]),
			("https://example.com/a'b", ["https://example.com/a'b"]),
			("https://example.com/a.b", ["https://example.com/a.b"]),
			("https://example.com?", ["https://example.com?"]),
			("https://example.com?#", ["https://example.com?#"]),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual(expected, _findUrls(text))

	def testExtractsUrlsFromCommonMarkup(self) -> None:
		"""Stop cleanly at HTML, Markdown, JSON, and plain-text boundaries."""
		cases = (
			('<a href="https://example.com/a?b=c#d">link</a>', ["https://example.com/a?b=c#d"]),
			("[docs](https://example.com/a(b)).", ["https://example.com/a(b)"]),
			('{"url": "https://example.com/a"}', ["https://example.com/a"]),
			("https://one.example^https://two.example", ["https://one.example", "https://two.example"]),
			("https://one.example\\https://two.example", ["https://one.example", "https://two.example"]),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual(expected, _findUrls(text))

	def testRejectsInvalidCandidates(self) -> None:
		"""Discard extracted candidates which are not usable URLs."""
		invalidUrls = (
			"http://:",
			"http:///path",
			"http://user@",
			"http://example.com:abc",
			"http://example.com:70000",
			"https://example.com/%ZZ",
		)
		for url in invalidUrls:
			with self.subTest(url=url):
				self.assertEqual([], _findUrls(url))

	def testSkipsInvalidCandidatesWithoutLosingLaterUrls(self) -> None:
		"""Continue scanning after structurally invalid URL candidates."""
		text = "http:///path https://example.com/%GG ftp://ftp.example.com/a www.example.com"
		self.assertEqual(
			["ftp://ftp.example.com/a", "www.example.com"],
			_findUrls(text),
		)

	def testPreservesExistingBehavior(self) -> None:
		"""Preserve case, Unicode, ordering, deduplication, and valid URL punctuation."""
		unicodeUrl = "https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84"
		text = f"HTTPS://example.com {unicodeUrl} https://example.com? HTTPS://example.com"
		self.assertEqual(
			["HTTPS://example.com", unicodeUrl, "https://example.com?"],
			_findUrls(text),
		)
		self.assertEqual([], _findUrls("wwwXexample.com"))
		self.assertEqual(["https://example.com"], _findUrls("HTML https://example.com</a>"))
		self.assertEqual(
			["http://a", "https://example.com"],
			_findUrls("http://a\nhttps://example.com"),
		)

	def testRequiresExactSupportedPrefixes(self) -> None:
		"""Require a supported scheme separator or a literal dot after www."""
		for text in (
			"http:/example.com",
			"https//example.com",
			"ftp:/example.com",
			"wwwXexample.com",
			"www-example.com",
			"www./path",
			"www.:80",
			"file://example.com",
			"mailto:user@example.com",
		):
			with self.subTest(text=text):
				self.assertEqual([], _findUrls(text))

	def testHandlesLongInputs(self) -> None:
		"""Handle long candidates and prefix-like text without changing the result."""
		longUrl = "https://example.com/" + ("a" * 65536)
		self.assertEqual([longUrl], _findUrls(longUrl))
		self.assertEqual([longUrl], _findUrls(longUrl + (")" * 65536)))
		balancedUrl = "https://example.com/" + ("(" * 512) + "a" + (")" * 512)
		self.assertEqual([balancedUrl], _findUrls(balancedUrl))
		self.assertEqual([], _findUrls("http:/" * 10000))


class SupportedUrlTests(unittest.TestCase):
	"""Tests for validating complete supported URLs."""

	def testAcceptsValidUrls(self) -> None:
		"""Accept representative valid URLs for every supported form."""
		validUrls = (
			"https://example.com",
			"HTTPS://example.com?",
			"WWW.example.com/path?q=1#fragment",
			"ftp://user:pass@example.com:21/a%20b",
			"http://[::1]",
			"http://[v1.a]",
			"http://[fe80::1%25eth0]/",
			"https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84",
			"http://127.0.0.1:0/",
			"http://user@example.com/",
			"http://example.com:00080/",
			"http://example.com:65535/path",
			"www.example.com:8080/path",
			"https://example.com/!$&'()*+,;=:@",
			"https://example.com/%00/%ff?x=%2F#fragment",
			"https://example.com?#",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))

	def testAcceptsEveryHexPercentEscape(self) -> None:
		"""Accept every two-digit hexadecimal percent escape."""
		hexDigits = "0123456789ABCDEF"
		for firstDigit in hexDigits:
			for secondDigit in hexDigits:
				url = f"https://example.com/%{firstDigit}{secondDigit}"
				with self.subTest(escape=url[-3:]):
					self.assertTrue(_isSupportedUrl(url))
					self.assertEqual([url], _findUrls(url))

	def testPortBoundaries(self) -> None:
		"""Accept only numeric ports in the range supported by URL parsing."""
		for port in (0, 1, 80, 65535):
			url = f"http://example.com:{port}/"
			with self.subTest(port=port):
				self.assertTrue(_isSupportedUrl(url))
		for port in ("-1", "+1", "1.5", "abc", "65536", "99999999999999999999"):
			url = f"http://example.com:{port}/"
			with self.subTest(port=port):
				self.assertFalse(_isSupportedUrl(url))

	def testRejectsInvalidUrls(self) -> None:
		"""Reject URLs with missing hosts, invalid ports, escapes, or raw delimiters."""
		invalidUrls = (
			"http://",
			"www.",
			"http://:",
			"http:///path",
			"http://user@",
			"http://[::1",
			"http://[]",
			"http://[:::]",
			"http://[gggg::1]",
			"http://[v.a]",
			"http://::1",
			"http://example.com:abc",
			"http://example.com:65536",
			"https://example.com/%",
			"https://example.com/%0",
			"https://example.com/%GG",
			"https://example.com^suffix",
		)
		for url in invalidUrls:
			with self.subTest(url=url):
				self.assertFalse(_isSupportedUrl(url))

	def testRejectsMalformedPercentEscapesEverywhere(self) -> None:
		"""Reject incomplete or non-hexadecimal percent escapes in URL components."""
		for escape in ("%", "%0", "%GG", "%0G", "%G0", "%%", "%-1"):
			for template in (
				"https://example.com/{}",
				"https://example.com/?q={}",
				"https://example.com/#{}",
				"https://user{}@example.com/",
			):
				url = template.format(escape)
				with self.subTest(url=url):
					self.assertFalse(_isSupportedUrl(url))

	def testRejectsUnsupportedSchemesAndMalformedAuthorities(self) -> None:
		"""Reject unsupported schemes and authorities which cannot identify a host."""
		invalidUrls = (
			"file://example.com/path",
			"nvdaremote://example.com",
			"mailto:user@example.com",
			"http:example.com",
			"http:/example.com",
			"https://?query",
			"https://#fragment",
			"www./path",
			"http://example.com\uff0fpath",
			"http://example.com\uff1a80",
		)
		for url in invalidUrls:
			with self.subTest(url=url):
				self.assertFalse(_isSupportedUrl(url))


class SourceCompatibilityTests(unittest.TestCase):
	"""Tests for compatibility with the add-on's declared minimum NVDA version."""

	def testSupportsPython37Grammar(self) -> None:
		"""Keep production code parseable by the Python version in NVDA 2021.1."""
		ast.parse(_URL_UTILS_PATH.read_text(encoding="utf-8"), feature_version=(3, 7))


if __name__ == "__main__":
	unittest.main()
