import pytest
from script import _extract_links_from_text


def test_extract_links_ez():
    text = "Links: https://arxiv.org/pdf/1234.5678v1 https://arxiv.org/abs/1234.5678 https://example.com/document.pdf "
    expected = {
        "arxiv_pdf": {"https://arxiv.org/pdf/1234.5678v1"},
        "arxiv_abs": {"https://arxiv.org/abs/1234.5678"},
        "pdf": {"https://example.com/document.pdf"},
    }
    assert _extract_links_from_text(text) == expected


def test_extracts_from_normal_markdown():
    url1 = "https://arxiv.org/pdf/1234.5678v1"
    url2 = "https://example.com/document.pdf"
    text = f"Check these links: [{url1}]({url1}) or a [named link]({url2}) "
    expected = {
        "arxiv_pdf": {url1},
        "arxiv_abs": set(),
        "pdf": {"https://example.com/document.pdf"},
    }
    assert _extract_links_from_text(text) == expected


def test_extract_links_with_no_links():
    text = "This is a text without any links."
    expected = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}
    assert _extract_links_from_text(text) == expected


def test_extract_links_with_invalid_links():
    text = "Invalid links: http://example.com, https://notarxiv.org/pdf/1234.5678"
    expected = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}
    assert _extract_links_from_text(text) == expected


def test_extract_links_with_empty_string():
    text = ""
    expected = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}
    assert _extract_links_from_text(text) == expected


@pytest.mark.parametrize("invalid_input", [None, 123, []])
def test_extract_links_with_invalid_input(invalid_input):
    with pytest.raises(TypeError):
        _extract_links_from_text(invalid_input)
