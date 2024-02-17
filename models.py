from dataclasses import dataclass
import base64, json
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

    def file_name(self):
        return self.url.split("/")[-1]

    def __str__(self):
        return f"""
            Paper(
                url={self.url},
                status={self.status},
                text_length={len(self.text) if self.text else 0}
                blob_size={len(self.blob) if self.blob else 0}
                pic_size={len(self.pic) if self.pic else 0}
            )
        """


class ProcessedPaper(Paper):
    def __init__(self, paper: Paper):
        super().__init__(paper.url, paper.status, paper.text, paper.blob, paper.pic)
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

    def extract_data(self, client, model_name: str, ctx_length: int):
        # LATER improve with 1 shotting
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": self.text[:ctx_length]}],
            functions=extractor,
            function_call={"name": "find_data"},
        )

        data = response.choices[0].message.function_call.arguments
        json_data = json.loads(data)

        self.title = json_data.get("title")
        self.keywords = json_data.get("keywords")
        self.authors = json_data.get("authors")
        self.abstract = json_data.get("abstract")
        self.published_date = json_data.get("published_date")
        self.summary = json_data.get("summary")
        self.institution = json_data.get("institution")
        self.location = json_data.get("location")

    def __str__(self):
        base_str = super().__str__()
        return f"""
            {base_str[:-1]}
                , embedding_size={len(self.embedding) if self.embedding else 0},
                title={self.title},
                keywords={self.keywords},
                authors={self.authors},
                abstract={self.abstract},
                published_date={self.published_date},
                summary={f"{self.summary[:100]}..." if self.summary else None},
                institution={self.institution},
                location={self.location}
            )
        """


extractor = [
    {
        "name": "find_data",
        "description": "finds data about the paper",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Extracts the title of the paper"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Extracts the keywords of the paper",
                },
                "authors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Extracts the authors of the paper",
                },
                "abstract": {"type": "string", "description": "Extracts the abstract of the paper"},
                "published_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Extracts the published date of the paper in format YYYY-MM-DD (as specific as possible)",
                },
                "summary": {
                    "type": "string",
                    "description": "Generates a summary of the paper. Directly describe what the paper is about.",
                },
                "institution": {
                    "type": "string",
                    "description": "Extracts the journal, institution, or organization of the paper",
                },
                "location": {
                    "type": "string",
                    "description": "Extracts the Central physical location of the paper if available, not a url.",
                },
                "doi": {
                    "type": "string",
                    "description": "Extracts the Digital Object Identifier of the paper",
                },
            },
        },
        "required": ["title"],
    }
]
