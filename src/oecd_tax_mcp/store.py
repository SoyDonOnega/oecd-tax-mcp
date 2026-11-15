"""Persist primary SDMX query snapshots for later derivation."""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any

from oecd_tax_mcp.fetch import cache_dir

_SNAP_DIR_NAME = "snapshots"


def _dir() -> Path:
    path = cache_dir() / _SNAP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", text).strip("-")
    return s[:80] or "snap"


def save_snapshot(payload: dict[str, Any]) -> str:
    """Write a snapshot; returns snapshot_id."""
    flow = payload.get("flow_ref") or "unknown"
    sid = f"{_slug(str(flow))}-{uuid.uuid4().hex[:8]}"
    record = {
        "snapshot_id": sid,
        "saved_at": time.time(),
        **payload,
    }
    (_dir() / f"{sid}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return sid


def load_snapshot(snapshot_id: str) -> dict[str, Any]:
    path = _dir() / f"{snapshot_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"snapshot not found: {snapshot_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_snapshots(limit: int = 30) -> list[dict[str, Any]]:
    files = sorted(_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: list[dict[str, Any]] = []
    for path in files[: max(1, min(limit, 100))]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        prov = data.get("provenance") or {}
        out.append(
            {
                "snapshot_id": data.get("snapshot_id") or path.stem,
                "flow_ref": data.get("flow_ref"),
                "key": data.get("key"),
                "start_period": data.get("start_period"),
                "end_period": data.get("end_period"),
                "row_count": len(data.get("all_rows") or data.get("rows") or []),
                "retrieved_at": prov.get("retrieved_at"),
                "cite": prov.get("cite"),
            }
        )
    return out
