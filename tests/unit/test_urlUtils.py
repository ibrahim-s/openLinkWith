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

	def testUnicodeDisplayControlsTerminateCandidates(self) -> None:
		"""Stop at invisible display controls and the fullwidth text separator."""
		terminators = (
			"\u061c",
			"\u200b",
			"\u200e",
			"\u200f",
			*(chr(value) for value in range(0x202A, 0x202F)),
			*(chr(value) for value in range(0x2060, 0x2065)),
			*(chr(value) for value in range(0x2066, 0x2070)),
			"\ufeff",
			"\uff5c",
		)
		for character in terminators:
			text = f"https://example.com{character}suffix"
			with self.subTest(codePoint=f"U+{ord(character):04X}"):
				self.assertEqual(["https://example.com"], _findUrls(text))
				self.assertFalse(_isSupportedUrl(text))

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

	def testKeepsScanningAfterAnInlineBoundary(self) -> None:
		"""Find a following URL when punctuation or an outer wrapper ends the previous URL."""
		cases = (
			(
				"http://one.example,http://two.example",
				["http://one.example", "http://two.example"],
			),
			(
				"https://one.example\uff0chttps://two.example",
				["https://one.example", "https://two.example"],
			),
			(
				"(http://one.example/path)https://two.example/path",
				["http://one.example/path", "https://two.example/path"],
			),
			(
				"\u300ahttps://one.example/\u8def\u5f84\u300bhttps://two.example/\u8def\u5f84",
				["https://one.example/\u8def\u5f84", "https://two.example/\u8def\u5f84"],
			),
			(
				"http://example.com:invalid,https://valid.example",
				["https://valid.example"],
			),
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

	def testHandlesLongUnicodeAndWrapperInputs(self) -> None:
		"""Keep Unicode hostname and wrapper scans linear on pathological input sizes."""
		unicodeUrl = "https://" + ("\ud55c.\uae00." * 10000) + "example"
		self.assertEqual([unicodeUrl], _findUrls(unicodeUrl))
		self.assertEqual(
			["https://example.com/path"],
			_findUrls(("(" * 10000) + "https://example.com/path" + (")" * 10000)),
		)
		adjacentUrls = [f"http://host{index}" for index in range(1000)]
		self.assertEqual(adjacentUrls, _findUrls(",".join(adjacentUrls)))


class EstablishedAutolinkerRegressionTests(unittest.TestCase):
	"""Regression cases adapted to this add-on from established URL autolinkers."""

	def testCmarkGfmTrailingPunctuationAndParentheses(self) -> None:
		"""Retain cmark-gfm URL punctuation and balanced-parenthesis behavior."""
		cases = (
			("(Scoped http://example.com/foo_bar)", "http://example.com/foo_bar"),
			("http://example.com/foo_bar...", "http://example.com/foo_bar"),
			(
				"www.google.com/search?q=Markup+(business)))",
				"www.google.com/search?q=Markup+(business)",
			),
			(
				"http://index-of.es/Android/Professional.Android.2.Application.Development.(Wrox,.2010).pdf",
				"http://index-of.es/Android/Professional.Android.2.Application.Development.(Wrox,.2010).pdf",
			),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual([expected], _findUrls(text))

	def testLinkifyItAuthorityAndTextSeparators(self) -> None:
		"""Stop at linkify-it-style host punctuation and fullwidth vertical bars."""
		cases = (
			("http://example.com,next", "http://example.com"),
			("http://example.com:8080,next", "http://example.com:8080"),
			("https://example.com\uff0c\u540e\u6587", "https://example.com"),
			("\uff5chttp://google.com\uff5cbar", "http://google.com"),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual([expected], _findUrls(text))
				self.assertFalse(_isSupportedUrl(text))

	def testLinkifyItMarkdownDestinationsDoNotMerge(self) -> None:
		"""Do not treat an at sign in a later Markdown destination as URL userinfo."""
		text = "[https](https://www.ibm.com)[mailto](mailto:someone@ibm.com)"
		self.assertEqual(["https://www.ibm.com"], _findUrls(text))

	def testOuterWrappersEndBeforeAdjacentText(self) -> None:
		"""End at a URL's outer wrapper even when prose follows without whitespace."""
		cases = (
			("(http://example.com/path)next", "http://example.com/path"),
			("[http://example.com/path]next", "http://example.com/path"),
			("'http://example.com/path'next", "http://example.com/path"),
			(
				"\u300ahttps://example.com/\u300a\u5185\u5c42\u300bpage\u300b\u540e\u6587",
				"https://example.com/\u300a\u5185\u5c42\u300bpage",
			),
			("\u201chttps://example.com/\u8def\u5f84\u201d\u540e\u6587", "https://example.com/\u8def\u5f84"),
			("\uff08https://example.com/\u8def\u5f84\uff09\u540e\u6587", "https://example.com/\u8def\u5f84"),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual([expected], _findUrls(text))

	def testVsCodeInternationalPathCases(self) -> None:
		"""Preserve CJK path characters covered by VS Code's LinkComputer regressions."""
		cases = (
			(
				"\u8bf7\u53c2\u9605 http://go.microsoft.com/fwlink/?LinkId=761051\u3002",
				"http://go.microsoft.com/fwlink/?LinkId=761051",
			),
			(
				"https://zh.wikipedia.org/wiki/\u3010\u6211\u63a8\u7684\u5b69\u5b50\u3011",
				"https://zh.wikipedia.org/wiki/\u3010\u6211\u63a8\u7684\u5b69\u5b50\u3011",
			),
			(
				"https://zh.wikipedia.org/wiki/\u300a\u65b0\u9752\u5e74\u300b\u7f16\u8f91\u90e8\u65e7\u5740",
				"https://zh.wikipedia.org/wiki/\u300a\u65b0\u9752\u5e74\u300b\u7f16\u8f91\u90e8\u65e7\u5740",
			),
			(
				"https://zh.wikipedia.org/wiki/\u201c\u5e38\u51ef\u7533\u201d\u8bef\u8bd1\u4e8b\u4ef6",
				"https://zh.wikipedia.org/wiki/\u201c\u5e38\u51ef\u7533\u201d\u8bef\u8bd1\u4e8b\u4ef6",
			),
			(
				"http://tree-mark.chips.jp/\u30ec\u30fc\u30ba\u30f3\uff06\u30d9\u30ea\u30fc\u30df\u30c3\u30af\u30b9",
				"http://tree-mark.chips.jp/\u30ec\u30fc\u30ba\u30f3\uff06\u30d9\u30ea\u30fc\u30df\u30c3\u30af\u30b9",
			),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual([expected], _findUrls(text))

	def testDjangoAndLinkifyInternationalHosts(self) -> None:
		"""Leave browser-facing IDNA policy to the user agent, as Django and linkify-it do."""
		validUrls = (
			"http://\U0001f453.ws",
			"http://\u272adf.ws/123",
			"https://example\U0001f600.com/path",
			"https://\u0789\u07a8\u0780\u07a7\u0783\u07aa.com",
			"https://www.\u0646\u0627\u0645\u0647\u200c\u0627\u06cc.com",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))
				self.assertEqual([url], _findUrls(url))


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


class InternationalUrlTests(unittest.TestCase):
	"""Tests for internationalized domain names and multilingual URL content."""

	def testAcceptsInternationalHostnamesAndPaths(self) -> None:
		"""Accept representative scripts in hostnames and paths without changing their text."""
		validUrls = (
			"https://m\u00fcnich.example/caf\u00e9",
			"https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84",
			"https://\u0645\u062b\u0627\u0644.\u0625\u062e\u062a\u0628\u0627\u0631/\u0645\u0633\u0627\u0631",
			"https://\u05d3\u05d5\u05d2\u05de\u05d4.\u05d9\u05e9\u05e8\u05d0\u05dc/\u05de\u05e1\u05dc\u05d5\u05dc",
			"https://\u043f\u0440\u0438\u043c\u0435\u0440.\u0440\u0444/\u043f\u0443\u0442\u044c",
			"https://\u03c0\u03b1\u03c1\u03ac\u03b4\u03b5\u03b9\u03b3\u03bc\u03b1.\u03b4\u03bf\u03ba\u03b9\u03bc\u03ae/\u03b4\u03b9\u03b1\u03b4\u03c1\u03bf\u03bc\u03ae",
			"https://\u0909\u0926\u093e\u0939\u0930\u0923.\u092d\u093e\u0930\u0924/\u092e\u093e\u0930\u094d\u0917",
			"https://\u0989\u09a6\u09be\u09b9\u09b0\u09a3.\u09ac\u09be\u0982\u09b2\u09be/\u09aa\u09a5",
			"https://\u0e15\u0e31\u0e27\u0e2d\u0e22\u0e48\u0e32\u0e07.\u0e44\u0e17\u0e22/\u0e40\u0e2a\u0e49\u0e19\u0e17\u0e32\u0e07",
			"https://\u4f8b\u3048.\u30c6\u30b9\u30c8/\u30d1\u30b9",
			"https://\uc608\uc2dc.\ud14c\uc2a4\ud2b8/\uacbd\ub85c",
			"www.\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84",
			"ftp://\u043f\u0440\u0438\u043c\u0435\u0440.\u0440\u0444/\u0444\u0430\u0439\u043b",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))
				self.assertEqual([url], _findUrls(url))

	def testAcceptsIdnaFormsAndContextCharacters(self) -> None:
		"""Accept IDNA dot forms, compatibility forms, and contextual join or punctuation characters."""
		validUrls = (
			"https://\u4f8b\u5b50\u3002\u4e2d\u56fd/path",
			"https://\uff45\uff58\uff41\uff4d\uff50\uff4c\uff45\uff0ecom/path",
			"https://xn--fsqu00a.xn--fiqs8s/path",
			"https://l\u00b7l.cat/path",
			"https://\u30c6\u30fb\u30b9\u30c8.jp/path",
			"https://\u05d0\u05f3.co.il/path",
			"https://cafe\u0301.example/path",
			"https://\u0645\u062b\u0627\u0644\u200c\u0646\u0627\u0645\u0647.com/path",
			"https://\u0915\u094d\u200d\u0937.com/path",
			"https://\u0375\u03b1.gr/path",
			"https://\u30fb\u30c6.jp/path",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))
				self.assertEqual([url], _findUrls(url))

	def testPreservesMultilingualPathQueryAndFragmentContent(self) -> None:
		"""Preserve Unicode punctuation and symbols after the authority component."""
		validUrls = (
			"https://example.com/\u4f60\u597d\uff0c\u4e16\u754c",
			"https://example.com/\u0645\u0631\u062d\u0628\u0627\u060c\u0627\u0644\u0639\u0627\u0644\u0645",
			"https://example.com/\u0645\u0631\u062d\u0628\u0627\u061f\u0646\u0639\u0645",
			"https://example.com/\u05e9\u05dc\u05d5\u05dd\u05be\u05e2\u05d5\u05dc\u05dd",
			"https://example.com/emoji/\U0001f600?q=\u65e5\u672c\u8a9e#\ud55c\uad6d\uc5b4",
			"https://example.com/cafe\u0301",
			"https://example.com/\u0915\u094d\u200d\u0937",
			"https://\u7528\u6237:\u5bc6\u7801@example.com/\u8d44\u6e90",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))
				self.assertEqual([url], _findUrls(url))

	def testStopsAtInternationalAuthorityBoundaries(self) -> None:
		"""Stop at multilingual prose punctuation and display controls after a hostname."""
		cases = (
			("https://example.com\uff0c\u540e\u6587", "https://example.com"),
			("https://example.com\u3001\u5f8c", "https://example.com"),
			("https://example.com\u060c\u0646\u0635", "https://example.com"),
			("https://example.com\u061f\u0646\u0635", "https://example.com"),
			("https://example.com\u055d\u0570\u0565\u057f\u0578", "https://example.com"),
			("https://example.com\u200bnext", "https://example.com"),
			("https://example.com\u200f\u0646\u0635", "https://example.com"),
			("https://example.com\u061c\u0646\u0635", "https://example.com"),
			("https://example.com\ufeffnext", "https://example.com"),
			("https://example.com\uff0fpath", "https://example.com"),
			("https://example.com\uff1a8080", "https://example.com"),
			("https://\u4f8b\u5b50.\u4e2d\u56fd\uff0c\u540e\u6587", "https://\u4f8b\u5b50.\u4e2d\u56fd"),
			("www.\u4f8b\u5b50.\u4e2d\u56fd\u060c\u0646\u0635", "www.\u4f8b\u5b50.\u4e2d\u56fd"),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertFalse(_isSupportedUrl(text))
				self.assertEqual([expected], _findUrls(text))

	def testTrimsInternationalProseWrappers(self) -> None:
		"""Trim multilingual sentence punctuation and wrappers while preserving balanced path content."""
		cases = (
			(
				"https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84\u3002",
				"https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84",
			),
			(
				"https://example.com/\u0645\u0633\u0627\u0631\u061f",
				"https://example.com/\u0645\u0633\u0627\u0631",
			),
			(
				"\u300ahttps://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84\u300b",
				"https://\u4f8b\u5b50.\u4e2d\u56fd/\u8def\u5f84",
			),
			(
				"\uff08https://example.com/\u8def\u5f84\uff08\u6d4b\u8bd5\uff09\uff09\u3002",
				"https://example.com/\u8def\u5f84\uff08\u6d4b\u8bd5\uff09",
			),
			("\u00abhttps://m\u00fcnich.example/caf\u00e9\u00bb", "https://m\u00fcnich.example/caf\u00e9"),
			("\u201chttps://example.com/\u8def\u5f84\u201d", "https://example.com/\u8def\u5f84"),
		)
		for text, expected in cases:
			with self.subTest(text=text):
				self.assertEqual([expected], _findUrls(text))

	def testTrimsRepresentativeScriptSentencePunctuation(self) -> None:
		"""Trim sentence punctuation used by representative writing systems."""
		for character in (
			"\u055d",
			"\u0589",
			"\u05c3",
			"\u060c",
			"\u061f",
			"\u0964",
			"\u0f0d",
			"\u104b",
			"\u1362",
			"\u3002",
			"\uff01",
		):
			with self.subTest(codePoint=f"U+{ord(character):04X}"):
				self.assertEqual(
					["https://example.com/path"],
					_findUrls(f"https://example.com/path{character}"),
				)

	def testPreservesPairedInternationalDelimitersInsidePaths(self) -> None:
		"""Preserve paired international delimiters in paths and trim them as outer wrappers."""
		pairs = (
			("\u00ab", "\u00bb"),
			("\u2018", "\u2019"),
			("\u201c", "\u201d"),
			("\u2039", "\u203a"),
			("\u3008", "\u3009"),
			("\u300a", "\u300b"),
			("\u300c", "\u300d"),
			("\u300e", "\u300f"),
			("\u3010", "\u3011"),
			("\u3014", "\u3015"),
			("\u3016", "\u3017"),
			("\u3018", "\u3019"),
			("\u301a", "\u301b"),
			("\uff08", "\uff09"),
			("\uff3b", "\uff3d"),
			("\uff5b", "\uff5d"),
			("\uff62", "\uff63"),
		)
		for opening, closing in pairs:
			pathUrl = f"https://example.com/{opening}path{closing}"
			with self.subTest(opening=opening, position="path"):
				self.assertEqual([pathUrl], _findUrls(pathUrl))
			with self.subTest(opening=opening, position="wrapper"):
				self.assertEqual(
					["https://example.com/path"],
					_findUrls(f"{opening}https://example.com/path{closing}suffix"),
				)


class SourceCompatibilityTests(unittest.TestCase):
	"""Tests for compatibility with the add-on's declared minimum NVDA version."""

	def testSupportsPython37Grammar(self) -> None:
		"""Keep production code parseable by the Python version in NVDA 2021.1."""
		ast.parse(_URL_UTILS_PATH.read_text(encoding="utf-8"), feature_version=(3, 7))


if __name__ == "__main__":
	unittest.main()
