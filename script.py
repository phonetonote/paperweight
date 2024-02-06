import os
import re
import argparse
from collections import namedtuple
from enum import Enum
from io import BytesIO
import fitz  # type: ignore
import requests  # type: ignore
import openai

BasePaper = namedtuple("BasePaper", ["url", "status", "text", "blob"])

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>")
)


class Paper(BasePaper):
    def __str__(self):
        return f"Paper(url={self.url}, status={self.status}, text_length={len(self.text)} blob_size={len(self.blob) if self.blob else 0})"


MAX_PDF_SIZE = 1 * 1024 * 1024 * 1024  #    ~1GB
MAX_TEXT_SIZE = 1 * 1024 * 1024  #          ~1MB

import struct

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = "cl100k_base"


def generate_embedding_for_text(text: str, client, model: str = EMBEDDING_MODEL) -> list[float]:
    truncated_text = text[:EMBEDDING_CTX_LENGTH]
    response = client.embeddings.create(model=model, input=[truncated_text])

    if response.data:
        embedding = response.data[0].embedding
        return embedding
    else:
        print("Failed to generate embedding.")
        return []


def encode_embedding(vector: list[float]) -> bytes:
    return struct.pack("f" * len(vector), *vector)


def fetch_and_extract_text_from_pdf(url):
    try:
        head_response = requests.head(url)
        content_length = int(head_response.headers.get("Content-Length", 0))
        status = "success"

        if content_length > MAX_PDF_SIZE:
            print(f"PDF is too large (>1GB), skipping blob storage for {url}")
            store_blob = False
            status = "pdf_too_large"
        else:
            store_blob = True

        response = requests.get(url)
        response.raise_for_status()

        print(f"Fetched url, processing PDF for {url}")

        text = ""
        with fitz.open(stream=BytesIO(response.content), filetype="pdf") as doc:
            for page in doc:
                if len(text) < MAX_TEXT_SIZE:
                    new_text = page.get_text()
                    if len(text) + len(new_text) > MAX_TEXT_SIZE:
                        text += new_text[: MAX_TEXT_SIZE - len(text)]
                        break
                    else:
                        text += new_text
                else:
                    break

        print("  Extracted text length in characters:", len(text))
        print("\n")
        return Paper(
            url=url, status=status, text=text, blob=response.content if store_blob else None
        )

    except requests.exceptions.RequestException as e:
        print(f"Request failed! {url}: {e}")
        print("\n")
        return Paper(url=url, status="unable_to_fetch", text="", blob=None)
    except Exception as e:
        print(f"  Error processing PDF!")
        print("\n")
        return Paper(url=url, status="processing_failed", text="", blob=None)


def process_paper(paper: Paper, client):
    if paper.status == "success" and paper.text:
        embedding = generate_embedding_for_text(paper.text, client)
        encoded_embedding = encode_embedding(embedding)
        return encoded_embedding
    else:
        print(f"Skipping embedding for {paper.url} due to status: {paper.status}")
        return None


def _extract_links_from_text(text):
    link_regex = re.compile(r"https?://[^\s]+\.pdf(?=\W|$)")
    papers = set()

    try:
        links = set(link_regex.findall(text))
        for link in links:
            paper = fetch_and_extract_text_from_pdf(link)
            print(paper)
            print("\n")
            papers.add(paper)

        for paper in papers:
            encoded_embedding = process_paper(paper, client)

        return papers
    except Exception as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        print(f"Error processing text: {snippet}\nException: {e}")
        return set()


# import sqlite3

# def create_table():
#     conn = sqlite3.connect('papers.db')
#     c = conn.cursor()
#     # Create table
#     c.execute('''CREATE TABLE IF NOT EXISTS papers
#                  (url TEXT, status TEXT, text TEXT, blob BLOB)''')
#     conn.commit()
#     conn.close()

# def insert_paper(paper):
#     conn = sqlite3.connect('papers.db')
#     c = conn.cursor()
#     # Insert a row of data
#     c.execute("INSERT INTO papers VALUES (?, ?, ?, ?)", (paper.url, paper.status, paper.text, paper.blob))
#     conn.commit()
#     conn.close()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract links from markdown files in the specified directory."
    )
    parser.add_argument("directory", help="Path to the directory containing markdown files")
    return parser.parse_args()


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


def main():
    args = parse_arguments()
    all_links = extract_links(args.directory)
    print("Extracted PDFs:", len(all_links))


if __name__ == "__main__":
    main()
