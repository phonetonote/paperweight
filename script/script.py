import os
import re


def extract_links(directory):
    accumulated_link_sets = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}

    for root, _, files in os.walk(directory):
        for file in filter(lambda f: f.endswith(".md"), files):
            try:
                with open(os.path.join(root, file), "r") as f:
                    file_content = f.read()
                    new_link_sets = _extract_links_from_text(file_content)
                    accumulated_link_sets = _merge_link_sets(accumulated_link_sets, new_link_sets)
            except Exception as e:
                print(f"Error reading file {file}: {e}")

    return (
        accumulated_link_sets["pdf"],
        accumulated_link_sets["arxiv_pdf"],
        accumulated_link_sets["arxiv_abs"],
    )


def _extract_links_from_text(text):
    link_sets = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}
    link_regex = re.compile(r"https?://[^\s,#?]+[^\s]*")

    links = link_regex.findall(text)
    for link in links:
        # Trim leading and trailing non-URL characters
        link = link.strip("(),[]{}")
        # Categorize the link
        if "arxiv.org/pdf/" in link:
            link_sets["arxiv_pdf"].add(link)
        elif "arxiv.org/abs/" in link:
            link_sets["arxiv_abs"].add(link)
        elif link.endswith(".pdf"):
            link_sets["pdf"].add(link)

    return link_sets


def _merge_link_sets(accumulated_link_sets, new_link_sets):
    for key in accumulated_link_sets:
        accumulated_link_sets[key] = accumulated_link_sets[key].union(new_link_sets[key])
    return accumulated_link_sets
