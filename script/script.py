import os
import re
import argparse


def extract_links(directory):
    all_links = set()

    for root, _, files in os.walk(directory):
        for file in filter(lambda f: f.endswith(".md"), files):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                links = _extract_links_from_text(file_content)
                all_links.update(links)
            except UnicodeDecodeError:
                print(f"Unicode decode error in file {file_path}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

    return all_links


def _extract_links_from_text(text):
    link_regex = re.compile(
        r"https?://(?:www\.)?arxiv\.org/[^\s]+(?=\W|$)|" r"https?://[^\s]+\.pdf(?=\W|$)"
    )

    try:
        return set(link_regex.findall(text))
    except Exception as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        print(f"Error processing text: {snippet}\nException: {e}")
        return set()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract links from markdown files in the specified directory."
    )
    parser.add_argument("directory", help="Path to the directory containing markdown files")
    return parser.parse_args()


def main():
    args = parse_arguments()
    all_links = extract_links(args.directory)
    print("Extracted Links:", all_links)


if __name__ == "__main__":
    main()
