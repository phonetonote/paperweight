import os, re, struct, logging
from typing import Set
from dotenv import load_dotenv
from openai import OpenAI
from models import MyFile, Paper, ProcessedPaper
from db import insert_paper, check_paper_exists
from text_extractor import fetch_and_extract_text_from_pdf


class LinkExtractor:
    EMBEDDING_MODEL = "text-embedding-3-small"
    LINK_REGEX = re.compile(r"https?://[^\s]+\.pdf(?=\W|$)")
    EMBEDDING_CTX_LENGTH = 8191

    def __init__(self, directory, db_name: str, model_name: str):
        load_dotenv()

        self.directory = directory
        self.client = OpenAI()
        self.db_name = db_name
        self.model_name = model_name

    def extract_links(self):
        print("scanning for md files")

        md_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.directory)
            for file in files
            if file.endswith(".md")
        ]
        print(f"found {len(md_files)} md files, searching for pdf links")

        for file_path in md_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    links: Set[str] = set(self.LINK_REGEX.findall(f.read()))
                for link in links:
                    if not check_paper_exists(link, self.db_name):
                        paper = fetch_and_extract_text_from_pdf(link)
                        print(f"processing {paper.file_name()}")
                        processed_paper = self.process_paper(paper)
                        file_create = os.path.getctime(file_path)
                        file_updated = os.path.getmtime(file_path)
                        my_file = MyFile(file_path, file_create, file_updated)
                        insert_paper(processed_paper, my_file, self.db_name)
                    else:
                        print(f"skipping {link.split('/')[-1]}, already exists")
            except Exception as e:
                logging.info(f"Error reading file {file_path}: {e}")
                logging.exception(e)

    def process_paper(self, paper: Paper) -> ProcessedPaper:
        processed_paper = ProcessedPaper(paper)

        if paper.status == "success" and paper.text:
            embedding = self.generate_embedding_for_text(paper.text)
            encoded_embedding = encode_embedding(embedding)
            processed_paper.embedding = encoded_embedding
            processed_paper.encode_pic()
            processed_paper.extract_data(self.client, self.model_name, self.EMBEDDING_CTX_LENGTH)
            processed_paper.status = "success_and_processed"

        return processed_paper

    def generate_embedding_for_text(self, text: str) -> list[float]:
        truncated_text = text[: self.EMBEDDING_CTX_LENGTH]
        response = self.client.embeddings.create(model=self.EMBEDDING_MODEL, input=[truncated_text])

        if response.data:
            embedding = response.data[0].embedding
            return embedding
        else:
            return []


def encode_embedding(vector: list[float]) -> bytes:
    return struct.pack("f" * len(vector), *vector)
