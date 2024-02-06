import pytest
from script import _extract_links_from_text


def test_extract_links_ez():
    text = "Links: https://arxiv.org/abs/1234.5678 https://example.com/document.pdf "
    expected = {
        "https://arxiv.org/abs/1234.5678",
        "https://example.com/document.pdf",
    }

    assert _extract_links_from_text(text) == expected


def test_extracts_from_normal_markdown():
    url2 = "https://example.com/document.pdf"
    text = f"Check these links with markdown [named link]({url2}) is great"
    assert _extract_links_from_text(text) == {url2}


def test_extract_links_with_no_links():
    text = "This is a text without any links."
    assert _extract_links_from_text(text) == set()


def test_extract_links_with_invalid_links():
    text = "Invalid links: http://example.com, https://notarxiv.org/pdf/1234.5678"
    assert _extract_links_from_text(text) == set()


def test_extract_links_with_empty_string():
    text = ""
    assert _extract_links_from_text(text) == set()
