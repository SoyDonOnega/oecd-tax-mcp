"""Download and cache OECD PDFs; extract text."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from pypdf import PdfReader

USER_AGENT = "oecd-tax-mcp/0.1 (+local MCP; research use; respects OECD ToS)"
DEFAULT_CACHE = Path(
    os.environ.get("OECD_TAX_MCP_CACHE", Path.home() / ".cache" / "oecd-tax-mcp")
)


def cache_dir() -> Path:
    path = DEFAULT_CACHE
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path(url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    return cache_dir() / f"{digest}.pdf"


def is_oecd_url(url: str) -> bool:
    """True for https URLs on oecd.org or one of its subdomains."""
    parsed = urlparse(str(url))
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "oecd.org" or host.endswith(".oecd.org"))


def fetch_pdf(url: str, *, force: bool = False) -> Path:
    # Boundary: this MCP fetches OECD only, before and after redirects.
    if not is_oecd_url(url):
        raise ValueError(f"Not an OECD URL (https on oecd.org only): {url}")
    dest = _cache_path(url)
    if dest.exists() and not force and dest.stat().st_size > 0:
        return dest
    with httpx.Client(
        follow_redirects=True,
        timeout=120.0,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"},
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        if not is_oecd_url(resp.url):
            raise ValueError(f"Redirected outside oecd.org: {resp.url}")
        ctype = (resp.headers.get("content-type") or "").lower()
        if "pdf" not in ctype and not url.lower().endswith(".pdf"):
            raise ValueError(
                f"URL did not return a PDF (content-type={ctype!r}). "
                "oecd.org HTML hubs are often Cloudflare-blocked; use catalog pdf_url."
            )
        dest.write_bytes(resp.content)
    return dest


def pdf_title(pdf_path: Path) -> str | None:
    """Title from the PDF's own metadata, if it has one."""
    meta = PdfReader(str(pdf_path)).metadata
    title = (meta.title or "").strip() if meta else ""
    return title or None


def extract_text(pdf_path: Path, *, max_pages: int | None = None) -> str:
    reader = PdfReader(str(pdf_path))
    pages = reader.pages
    if max_pages is not None:
        pages = pages[:max_pages]
    chunks: list[str] = []
    for i, page in enumerate(pages):
        text = page.extract_text() or ""
        chunks.append(f"\n--- page {i + 1} ---\n{text}")
    return "".join(chunks).strip()


def find_snippets(text: str, query: str, *, window: int = 500, limit: int = 8) -> list[str]:
    q = (query or "").strip()
    if not q or not text:
        return []
    # Prefer paragraph-like tokens (e.g. 6.32) as whole-word-ish matches
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    out: list[str] = []
    for m in pattern.finditer(text):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        snippet = text[start:end].strip()
        out.append(snippet)
        if len(out) >= limit:
            break
    return out


def paginate(text: str, *, max_chars: int, page: int) -> tuple[str, dict]:
    max_chars = max(500, min(max_chars, 100_000))
    page = max(1, page)
    total = len(text)
    start = (page - 1) * max_chars
    end = min(total, start + max_chars)
    meta = {
        "page": page,
        "max_chars": max_chars,
        "total_chars": total,
        "truncated": end < total or start > 0,
        "has_more": end < total,
    }
    return text[start:end], meta
