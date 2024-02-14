from dataclasses import dataclass


@dataclass
class MyFile:
    full_path: str
    file_creation_date: float
    file_modified_date: float

    def __str__(self):
        return f"""
            MyFile(
                full_path={self.full_path},
                file_creation_date={self.file_creation_date},
                file_modified_date={self.file_modified_date},
            )
        """


class Paper:
    def __init__(self, url, status, text, blob):
        self.url = url
        self.status = status
        self.text = text
        self.blob = blob

    def __str__(self):
        return f"""
            Paper(
                url={self.url},
                status={self.status},
                text_length={len(self.text)}
                blob_size={len(self.blob) if self.blob else 0}
            )
        """


class ProcessedPaper:
    def __init__(self, paper: Paper):
        # self.file = paper.file
        self.url = paper.url
        self.status = paper.status
        self.text = paper.text
        self.blob = paper.blob
        self.embedding: bytes = b""

        self.title = None
        self.categories = []
        self.authors = []
        self.abstract = None
        self.published_date = None
        self.summary = None
        self.institution = None
        self.location = None

    def update_from_json(self, json_data):
        self.title = json_data.get("title")
        self.categories = json_data.get("categories")
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
                categories={self.categories},
                authors={self.authors},
                abstract={self.abstract},
                published_date={self.published_date},
                summary={f"{self.summary[0:100]}..." if self.summary else None},
                institution={self.institution},
                location={self.location}
            )
        """
