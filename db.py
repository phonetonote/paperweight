import logging, json, sqlite3
from models import MyFile, ProcessedPaper
import pandas as pd
from tenacity import retry, wait_random_exponential, stop_after_attempt


def init_db(db_name: str):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # LATER use `BLOB CHECK (jsonb_valid(authors))`
    # to validate jsonb on keywords and authors -
    # https://sqlite.org/forum/forumpost/fa6f64e3dc1a5d97
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            url TEXT PRIMARY KEY,
            title TEXT,
            authors TEXT,
            keywords TEXT,
            abstract TEXT,
            published_date TEXT,
            summary TEXT,
            institution TEXT,
            location TEXT,
            status TEXT,
            text TEXT,
            blob BLOB,
            embedding BLOB,
            encoded_pic TEXT,
            file_path TEXT,
            created_at FLOAT,
            updated_at FLOAT
        )
    """
    )
    conn.commit()
    conn.close()


def insert_paper(processed_paper: ProcessedPaper, my_file: MyFile, db_name: str):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        processed_paper.encoded_pic

        c.execute(
            """
            INSERT INTO papers (
                url, status, text, blob, title, keywords, authors,
                abstract, published_date, summary, institution, location,
                embedding, encoded_pic, file_path, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                processed_paper.url,
                processed_paper.status,
                processed_paper.text,
                processed_paper.blob,
                processed_paper.title,
                json.dumps(processed_paper.keywords),
                json.dumps(processed_paper.authors),
                processed_paper.abstract,
                processed_paper.published_date,
                processed_paper.summary,
                processed_paper.institution,
                processed_paper.location,
                processed_paper.embedding,
                processed_paper.encoded_pic,
                my_file.full_path,
                my_file.created_at,
                my_file.updated_at,
            ),
        )
        conn.commit()
    except Exception as e:
        logging.info(f"Error inserting {processed_paper.url}: {e}")
    finally:
        conn.close()


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
def fetch_papers_as_df(db_name: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_name)
        df = pd.read_sql_query("SELECT * FROM papers", conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        logging.info(f"Encountered a SQLite error: {e}, retrying...")
        logging.exception(e)
        raise  # re-raising the exception to allow the retry mechanism to kick in


def check_paper_exists(url, db_name):
    conn = sqlite3.connect(db_name)

    c = conn.cursor()
    c.execute("SELECT url FROM papers WHERE url = ?", (url,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
