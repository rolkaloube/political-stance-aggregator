import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from typing import Iterable, Optional


DB_PATH = "web_docs.db"
USER_AGENT = "Mozilla/5.0 (compatible; SimpleScraper/1.0; +https://example.com)"


def create_database(db_path: str = DB_PATH) -> None:
    """Create the SQLite database and table if they do not exist."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT,
                title TEXT,
                status_code INTEGER,
                fetched_at TEXT NOT NULL,
                content TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_domain ON documents(domain)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_fetched_at ON documents(fetched_at)")
        conn.commit()
    finally:
        conn.close()


def fetch_html(url: str, timeout: int = 20) -> tuple[int, str]:
    """Download a web page and return status code and HTML."""
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.status_code, response.text


def extract_text_and_title(html: str) -> tuple[Optional[str], str]:
    """Extract page title and visible text from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    # Get visible text
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    cleaned_text = "\n".join(line for line in lines if line)

    return title, cleaned_text


def save_document(
    url: str,
    status_code: int,
    title: Optional[str],
    content: str,
    db_path: str = DB_PATH
) -> None:
    """Insert or update a document in SQLite."""
    domain = urlparse(url).netloc
    fetched_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            INSERT INTO documents (url, domain, title, status_code, fetched_at, content)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                domain = excluded.domain,
                title = excluded.title,
                status_code = excluded.status_code,
                fetched_at = excluded.fetched_at,
                content = excluded.content
        """, (url, domain, title, status_code, fetched_at, content))
        conn.commit()
    finally:
        conn.close()


def scrape_and_store(url: str, db_path: str = DB_PATH) -> None:
    """Fetch a single page, extract text, and store it."""
    try:
        status_code, html = fetch_html(url)
        title, content = extract_text_and_title(html)
        save_document(url, status_code, title, content, db_path=db_path)
        print(f"Saved: {url}")
    except requests.RequestException as exc:
        print(f"Request failed for {url}: {exc}")
    except Exception as exc:
        print(f"Unexpected error for {url}: {exc}")


def scrape_many(urls: Iterable[str], db_path: str = DB_PATH) -> None:
    """Scrape multiple URLs."""
    create_database(db_path)
    for url in urls:
        scrape_and_store(url, db_path=db_path)


if __name__ == "__main__":
    urls_to_scrape = [
        "https://example.com",
        "https://www.python.org",
    ]
    scrape_many(urls_to_scrape)
