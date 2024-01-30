import os
import re


def extract_links(directory):
    pdf_links = set()
    arxiv_pdf_links = set()
    arxiv_abs_links = set()

    link_regex = re.compile(
        r"(https?://(?:www\.)?(?:arxiv\.org/(?:abs|pdf)/[^\s/#?]+(?:v\d+)?[^\s]*|[^ \s]+\.pdf))"
    )

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                try:
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        links = link_regex.findall(content)
                        for link in links:
                            if "arxiv.org/pdf/" in link:
                                arxiv_pdf_links.add(link)
                            elif "arxiv.org/abs/" in link:
                                arxiv_abs_links.add(link)
                            elif link.endswith(".pdf"):
                                pdf_links.add(link)
                except Exception as e:
                    print(f"Error reading file {file}: {e}")

    return pdf_links, arxiv_pdf_links, arxiv_abs_links


pdf_links, arxiv_pdf_links, arxiv_abs_links = extract_links("data")

print("General PDF Links:")
for link in pdf_links:
    print(link)

print("\nArXiv PDF Links:")
for link in arxiv_pdf_links:
    print(link)

print("\nArXiv Abstract Links:")
for link in arxiv_abs_links:
    print(link)
