"""Discover -> classify -> verify -> store -> notify."""
import json
from pathlib import Path

from . import classify, db, notify, tinyfish_client, verify
from .sources import SOURCES

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_notices.json"


def _load(source: dict, demo: bool) -> list[dict]:
    if demo:
        return [n for n in json.loads(SAMPLE.read_text()) if n["source"] == source["id"]]
    return tinyfish_client.extract_notices(source)


def refresh(demo: bool = True, check_links: bool = False) -> list[dict]:
    """Returns the notices that were new in this run."""
    new_rows = []
    for src in SOURCES:
        for n in _load(src, demo):
            title, date = n["title"], db.normalize_date(n.get("published_date"))
            c = classify.classify(title)
            ok = verify.is_official(src["url"])
            if ok and check_links and n.get("pdf_url"):
                ok = verify.link_opens(n["pdf_url"])
            row = {
                "id": db.notice_id(src["id"], title, date), "source": src["id"],
                "exam": n.get("exam_name"), "title": title, "published_date": date,
                "notice_type": c["notice_type"], "summary": c["summary"],
                "pdf_url": n.get("pdf_url"), "source_url": src["url"], "verified": int(ok),
            }
            if db.insert_if_new(row):
                new_rows.append(row)
                notify.send_telegram(row)
    return new_rows
