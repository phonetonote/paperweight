import sqlite3
import json

# TODO move to args
DB_NAME = "papers.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # LATER use `BLOB CHECK (jsonb_valid(authors))`
    # to validate jsonb on categories and authors -
    # https://sqlite.org/forum/forumpost/fa6f64e3dc1a5d97
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            url TEXT PRIMARY KEY,
            title TEXT,
            authors BLOB,
            categories BLOB,
            abstract TEXT,
            published_date TEXT,
            summary TEXT,
            institution TEXT,
            location TEXT,
            status TEXT,
            text TEXT,
            blob BLOB,
            embedding BLOB
        )
    """
    )
    conn.commit()
    conn.close()


def insert_paper(processed_paper):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO papers (url, status, text, blob, title, categories, authors, abstract, published_date, summary, institution, location, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                processed_paper.url,
                processed_paper.status,
                processed_paper.text,
                processed_paper.blob,
                processed_paper.title,
                json.dumps(processed_paper.categories),
                json.dumps(processed_paper.authors),
                processed_paper.abstract,
                processed_paper.published_date,
                processed_paper.summary,
                processed_paper.institution,
                processed_paper.location,
                processed_paper.embedding,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Paper with URL {processed_paper.url} already exists in the database. Error: {e}")
    finally:
        conn.close()


def check_paper_exists(url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT url FROM papers WHERE url = ?", (url,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
