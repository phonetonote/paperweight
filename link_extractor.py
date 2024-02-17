import os
import re
import json
import struct
from typing import Set
from dotenv import load_dotenv
from openai import OpenAI
from models import MyFile, Paper, ProcessedPaper
from db import insert_paper, check_paper_exists
from text_extractor import fetch_and_extract_text_from_pdf


class LinkExtractor:
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_CTX_LENGTH = 8191
    LINK_REGEX = re.compile(r"https?://[^\s]+\.pdf(?=\W|$)")

    def __init__(self, directory, db_name: str, model_name: str):
        load_dotenv()

        self.directory = directory
        self.client = OpenAI()
        self.db_name = db_name
        self.model_name = model_name

    def extract_links(self):
        for root, _, files in os.walk(self.directory):
            for file in filter(lambda f: f.endswith(".md"), files):
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        links: Set[str] = set(self.LINK_REGEX.findall(f.read()))
                    for link in links:
                        if not check_paper_exists(link, self.db_name):
                            paper = fetch_and_extract_text_from_pdf(link)
                            processed_paper = self.process_paper(paper)
                            processed_paper.encode_pic()
                            json_data = self.get_metadata(processed_paper)
                            processed_paper.update_from_json(json_data)
                            file_create = os.path.getctime(file_path)
                            file_updated = os.path.getmtime(file_path)
                            my_file = MyFile(file_path, file_create, file_updated)
                            insert_paper(processed_paper, my_file, self.db_name)
                            print(processed_paper)
                        else:
                            print(f"{link} already in db, skipping")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    def process_paper(self, paper: Paper) -> ProcessedPaper:
        processed_paper = ProcessedPaper(paper)

        if paper.status == "success" and paper.text:
            embedding = self.generate_embedding_for_text(paper.text)
            encoded_embedding = encode_embedding(embedding)
            processed_paper.embedding = encoded_embedding
            processed_paper.status = "success_with_embedding"

        return processed_paper

    def generate_embedding_for_text(self, text: str) -> list[float]:
        truncated_text = text[: self.EMBEDDING_CTX_LENGTH]
        response = self.client.embeddings.create(model=self.EMBEDDING_MODEL, input=[truncated_text])

        if response.data:
            embedding = response.data[0].embedding
            return embedding
        else:
            return []

    def get_metadata(self, processed_paper):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": processed_paper.text[: self.EMBEDDING_CTX_LENGTH]}
            ],
            functions=extractor,
            function_call={"name": "find_data"},
        )

        data = response.choices[0].message.function_call.arguments
        json_data = json.loads(data)
        return json_data


def encode_embedding(vector: list[float]) -> bytes:
    return struct.pack("f" * len(vector), *vector)


extractor = [
    {
        "name": "find_data",
        "description": "finds data about the paper",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the paper"},
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Categories of the paper",
                },
                "authors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Authors of the paper",
                },
                "abstract": {"type": "string", "description": "Abstract of the paper"},
                "published_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Published date of the paper in format YYYY-MM-DD (as specific as possible)",
                },
                "summary": {
                    "type": "string",
                    "description": "Summary of the paper. If it is an academic paper with an abstract, provide the abstract here. Otherwise, describe what the paper is about.",
                },
                "instituion": {
                    "type": "string",
                    "description": "Journal, institution, or organization of the paper",
                },
                "location": {
                    "type": "string",
                    "description": "Central physical location of the paper if available, not a url.",
                },
            },
        },
        "required": ["title"],
    }
]
