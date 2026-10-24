"""Source verification: official-domain check and link check."""
from urllib.parse import urlparse

import httpx

from .config import OFFICIAL_SUFFIXES


def is_official(url: str | None) -> bool:
    """True only for .gov.in / .nic.in hosts. Always pass the URL we requested,
    not the final resolved URL (Fetch can resolve to a raw IP address)."""
    if not url:
        return False
    host = (urlparse(url).hostname or "").lower()
    return host in ("gov.in", "nic.in") or host.endswith(OFFICIAL_SUFFIXES)


def link_opens(url: str | None, timeout: float = 10.0) -> bool:
    """True if the URL returns a non-error response."""
    if not url:
        return False
    try:
        r = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"Range": "bytes=0-1023"})
        return r.status_code < 400
    except httpx.HTTPError:
        return False
