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
			"http://example.com:65535/path",
		)
		for url in validUrls:
			with self.subTest(url=url):
				self.assertTrue(_isSupportedUrl(url))

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


class SourceCompatibilityTests(unittest.TestCase):
	"""Tests for compatibility with the add-on's declared minimum NVDA version."""

	def testSupportsPython37Grammar(self) -> None:
		"""Keep production code parseable by the Python version in NVDA 2021.1."""
		ast.parse(_URL_UTILS_PATH.read_text(encoding="utf-8"), feature_version=(3, 7))


if __name__ == "__main__":
	unittest.main()
