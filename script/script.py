import os
import re
import argparse


def extract_links(directory):
    accumulated_link_sets = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}

    for root, _, files in os.walk(directory):
        for file in filter(lambda f: f.endswith(".md"), files):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                new_link_sets = _extract_links_from_text(file_content)
                accumulated_link_sets = _merge_link_sets(accumulated_link_sets, new_link_sets)
            except UnicodeDecodeError:
                print(f"Unicode decode error in file {file_path}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

    return (
        accumulated_link_sets["pdf"],
        accumulated_link_sets["arxiv_pdf"],
        accumulated_link_sets["arxiv_abs"],
    )


def _extract_links_from_text(text):
    link_sets = {"arxiv_pdf": set(), "arxiv_abs": set(), "pdf": set()}

    link_regex = re.compile(
        r"(https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/[^\s/#?]+(?:v\d+)?)(?=\W|$)|(https?://[^\s]+\.pdf)(?=\W|$)"
    )

    try:
        links = link_regex.findall(text)
        for link_group in links:
            link = next(sublink for sublink in link_group if sublink)
            if "arxiv.org/pdf/" in link:
                link_sets["arxiv_pdf"].add(link)
            elif "arxiv.org/abs/" in link:
                link_sets["arxiv_abs"].add(link)
            elif link.endswith(".pdf"):
                link_sets["pdf"].add(link)
    except Exception as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        print(f"Error processing text: {snippet}\nException: {e}")

    return link_sets


def _merge_link_sets(accumulated_link_sets, new_link_sets):
    for key in accumulated_link_sets:
        accumulated_link_sets[key] = accumulated_link_sets[key].union(new_link_sets[key])
    return accumulated_link_sets


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract links from markdown files in the specified directory."
    )
    parser.add_argument("directory", help="Path to the directory containing markdown files")
    return parser.parse_args()


def main():
    args = parse_arguments()
    pdf_links, arxiv_pdf_links, arxiv_abs_links = extract_links(args.directory)

    print("PDF Links:", pdf_links)
    print("ArXiv PDF Links:", arxiv_pdf_links)
    print("ArXiv Abstract Links:", arxiv_abs_links)


if __name__ == "__main__":
    main()
