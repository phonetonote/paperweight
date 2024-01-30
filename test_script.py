import pytest
import os
from script import extract_links


def test_extract_links(tmp_path):
    # Create mock files with links
    links = {
        "file1.md": "https://arxiv.org/pdf/1234.5678v1\nhttps://example.com/document.pdf",
        "file2.md": "https://arxiv.org/abs/1234.5678\nhttp://example.com/another_document.pdf",
    }

    for filename, content in links.items():
        with open(tmp_path / filename, "w") as f:
            f.write(content)

    # Call the function with the temporary directory
    pdf_links, arxiv_pdf_links, arxiv_abs_links = extract_links(tmp_path)

    # Assertions to check if the function is working as expected
    assert "https://arxiv.org/pdf/1234.5678v1" in arxiv_pdf_links
    assert "https://example.com/document.pdf" in pdf_links
    assert "https://arxiv.org/abs/1234.5678" in arxiv_abs_links

    # Optionally, check if all links were found
    assert len(pdf_links) == 2
    assert len(arxiv_pdf_links) == 1
    assert len(arxiv_abs_links) == 1
