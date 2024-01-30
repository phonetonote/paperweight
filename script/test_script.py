import pytest
from script import _extract_links_from_text


def test_extract_links_with_surrounding_characters():
    text = "Links: https://arxiv.org/pdf/1234.5678v1 https://arxiv.org/abs/1234.5678 https://example.com/document.pdf "
    expected = {
        "arxiv_pdf": {"https://arxiv.org/pdf/1234.5678v1"},
        "arxiv_abs": {"https://arxiv.org/abs/1234.5678"},
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