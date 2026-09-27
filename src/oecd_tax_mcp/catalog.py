"""Load and search the curated OECD tax instrument catalogue."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent
_CANDIDATES = [
    _ROOT / "data" / "catalog.json",
    _ROOT.parent.parent / "data" / "catalog.json",
]


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    for path in _CANDIDATES:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(
        "catalog.json not found; expected under package data/ or repo data/"
    )


def instruments() -> list[dict[str, Any]]:
    return list(load_catalog()["instruments"])


def dataset_note() -> str:
    return str(load_catalog().get("dataset_note", ""))


def _haystack(inst: dict[str, Any]) -> str:
    parts = [
        inst.get("id", ""),
        inst.get("title", ""),
        inst.get("cite_as", ""),
        inst.get("notes", ""),
        " ".join(inst.get("aliases") or []),
        " ".join(inst.get("topics") or []),
        str(inst.get("year", "")),
        inst.get("authority", ""),
    ]
    return " ".join(parts).lower()


def search_instruments(query: str, limit: int = 10) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return instruments()[:limit]
    tokens = [t for t in re.split(r"\s+", q) if t]
    scored: list[tuple[int, dict[str, Any]]] = []
    for inst in instruments():
        hay = _haystack(inst)
        score = 0
        if q in hay:
            score += 10
        for t in tokens:
            if t in hay:
                score += 3
            if inst.get("id", "").lower() == t or t in [
                a.lower() for a in (inst.get("aliases") or [])
            ]:
                score += 8
        if score:
            scored.append((score, inst))
    scored.sort(key=lambda x: (-x[0], -int(x[1].get("year") or 0)))
    return [inst for _, inst in scored[:limit]]


def resolve_instrument(identifier: str) -> dict[str, Any] | None:
    raw = (identifier or "").strip()
    if not raw:
        return None
    key = raw.lower()
    for inst in instruments():
        if inst.get("id", "").lower() == key:
            return inst
        if key in [a.lower() for a in (inst.get("aliases") or [])]:
            return inst
        if inst.get("doi") and key in {
            inst["doi"].lower(),
            f"doi:{inst['doi']}".lower(),
            f"https://doi.org/{inst['doi']}".lower(),
        }:
            return inst
    # fuzzy: unique substring on id/title
    hits = search_instruments(raw, limit=5)
    if len(hits) == 1:
        return hits[0]
    for h in hits:
        if h.get("id", "").lower() == key or key in h.get("title", "").lower():
            return h
    return None


def public_meta(inst: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": inst["id"],
        "title": inst["title"],
        "year": inst.get("year"),
        "authority": inst.get("authority"),
        "topics": inst.get("topics") or [],
        "aliases": inst.get("aliases") or [],
        "landing_url": inst.get("landing_url"),
        "pdf_url": inst.get("pdf_url"),
        "doi": inst.get("doi"),
        "cite_as": inst.get("cite_as"),
        "notes": inst.get("notes"),
        "jurisdiction": "OECD/international",
        "dataset_note": dataset_note(),
    }
