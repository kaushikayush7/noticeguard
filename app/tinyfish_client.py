"""All TinyFish calls live here. Search + Fetch are free; Agent runs use credits."""
from tinyfish import TinyFish

from .config import OFFICIAL_SUFFIXES

_SCHEMA = {
    "type": "object",
    "properties": {"notices": {"type": "array", "items": {"type": "object", "properties": {
        "title": {"type": "string"}, "published_date": {"type": "string"},
        "exam_name": {"type": ["string", "null"]}, "pdf_url": {"type": ["string", "null"]}},
        "required": ["title", "published_date"]}}},
    "required": ["notices"],
}


def _client() -> TinyFish:
    return TinyFish()  # reads TINYFISH_API_KEY


def extract_notices(source: dict) -> list[dict]:
    """Agent: navigate a notice board that has no API and return structured notices."""
    resp = _client().agent.run(goal=source["goal"], url=source["url"], output_schema=_SCHEMA)
    result = getattr(resp, "result", None) or {}
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if isinstance(result.get("notices"), list):
            return result["notices"]
        for v in result.values():
            if isinstance(v, list):
                return v
    return []


def fetch_text(url: str) -> str:
    """Fetch: turn a page or PDF into clean markdown for the LLM."""
    resp = _client().fetch.get_contents([url], format="markdown")
    if not resp.results:
        return ""
    return getattr(resp.results[0], "text", "") or ""


def discover(query: str, limit: int = 10) -> list[dict]:
    """Search: find candidate pages, flag which ones are on official domains."""
    resp = _client().search.query(query)
    out = []
    for r in resp.results[:limit]:
        url = getattr(r, "url", "") or ""
        host = url.split("/")[2] if url.startswith("http") and len(url.split("/")) > 2 else ""
        out.append({"title": getattr(r, "title", ""), "url": url,
                    "official": host.endswith(OFFICIAL_SUFFIXES)})
    return out
