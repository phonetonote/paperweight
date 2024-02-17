from dataclasses import dataclass
import base64
from typing import Optional
from fitz import Pixmap


@dataclass
class MyFile:
    full_path: str
    created_at: float
    updated_at: float

    def __str__(self):
        return f"""
            MyFile(
                full_path={self.full_path},
                created_at={self.created_at},
                updated_at={self.updated_at},
            )
        """


class Paper:
    def __init__(
        self,
        url: str,
        status: str,
        text: Optional[str] = None,
        blob: Optional[bytes] = None,
        pic: Optional[Pixmap] = None,
    ):
        self.url = url
        self.status = status
        self.text = text
        self.blob = blob
        self.pic = pic

    def __str__(self):
        return f"""
            Paper(
                url={self.url},
                status={self.status},
                text_length={len(self.text)}
                blob_size={len(self.blob) if self.blob else 0}
                pic_size={len(self.pic) if self.pic else 0}
            )
        """


class ProcessedPaper:
    def __init__(self, paper: Paper):
        self.url = paper.url
        self.status = paper.status
        self.text = paper.text
        self.blob = paper.blob
        self.pic = paper.pic
        self.encoded_pic: Optional[str] = None
        self.embedding: bytes = b""
        self.title = None
        self.keywords = []
        self.authors = []
        self.abstract = None
        self.published_date = None
        self.summary = None
        self.institution = None
        self.location = None

    def encode_pic(self):
        if self.pic is None:
            return

        image_bytes = self.pic.tobytes("png")
        self.encoded_pic = base64.b64encode(image_bytes).decode("utf-8")

    def update_from_json(self, json_data):
        self.title = json_data.get("title")
        self.keywords = json_data.get("keywords")
        self.authors = json_data.get("authors")
        self.abstract = json_data.get("abstract")
        self.published_date = json_data.get("published_date")
        self.summary = json_data.get("summary")
        self.institution = json_data.get("institution")
        self.location = json_data.get("location")

    def __str__(self):
        return f"""
            ProcessedPaper(
                url={self.url},
                status={self.status},
                text_length={len(self.text)},
                blob_size={len(self.blob) if self.blob else 0},
                embedding_size={len(self.embedding) if self.embedding else 0},
                title={self.title},
                keywords={self.keywords},
                authors={self.authors},
                abstract={self.abstract},
                published_date={self.published_date},
                summary={f"{self.summary[0:100]}..." if self.summary else None},
                institution={self.institution},
                location={self.location}
            )
        """
