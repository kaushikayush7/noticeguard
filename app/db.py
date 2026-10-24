import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import DB_PATH

SCHEMA = """CREATE TABLE IF NOT EXISTS notices (
  id TEXT PRIMARY KEY, source TEXT, exam TEXT, title TEXT, published_date TEXT,
  notice_type TEXT, summary TEXT, pdf_url TEXT, source_url TEXT,
  verified INTEGER, first_seen TEXT)"""


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    with conn() as c:
        c.execute(SCHEMA)


def notice_id(source: str, title: str, date: str) -> str:
    return hashlib.sha1(f"{source}|{title}|{date}".encode()).hexdigest()[:16]


def normalize_date(s: str | None) -> str:
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime((s or "").strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return (s or "").strip()


def insert_if_new(row: dict) -> bool:
    """Returns True if the notice was new (i.e. should trigger an alert)."""
    with conn() as c:
        cur = c.execute(
            "INSERT OR IGNORE INTO notices VALUES (:id,:source,:exam,:title,:published_date,:notice_type,"
            ":summary,:pdf_url,:source_url,:verified,:first_seen)",
            {**row, "first_seen": datetime.now(timezone.utc).isoformat()})
        return cur.rowcount == 1


def list_alerts(notice_type: str | None = None) -> list[dict]:
    q, args = "SELECT * FROM notices", []
    if notice_type and notice_type != "all":
        q, args = q + " WHERE notice_type = ?", [notice_type]
    with conn() as c:
        return [dict(r) for r in c.execute(q + " ORDER BY published_date DESC, first_seen DESC", args)]
