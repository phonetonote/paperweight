from io import BytesIO
import requests
from fitz import open as fitzopen
from models import Paper

MAX_PDF_SIZE = 1 * 1024 * 1024 * 1024  #    ~1GB
MAX_TEXT_SIZE = 1 * 1024 * 1024  #          ~1MB


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

        text = ""
        with fitzopen(stream=BytesIO(response.content), filetype="pdf") as doc:
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

        return Paper(
            url=url, status=status, text=text, blob=response.content if store_blob else None
        )

    except requests.exceptions.RequestException as e:
        print(f"Request failed! {url}: {e}")
        print("\n")
        return Paper(url=url, status="unable_to_fetch", text="", blob=None)
    except Exception as e:
        print(f"  Error processing PDF {url}: {e}")
        return Paper(url=url, status="processing_failed", text="", blob=None)
