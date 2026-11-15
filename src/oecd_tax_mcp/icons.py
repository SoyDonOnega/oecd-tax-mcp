"""Load MCP server icons from packaged / repo assets."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

from mcp.types import Icon

_ROOT = Path(__file__).resolve().parent
_CANDIDATES = [
    _ROOT / "assets" / "logo.png",
    _ROOT.parent.parent / "assets" / "logo.png",
]


@lru_cache(maxsize=1)
def server_icons() -> list[Icon]:
    for path in _CANDIDATES:
        if not path.is_file():
            continue
        raw = path.read_bytes()
        b64 = base64.standard_b64encode(raw).decode("ascii")
        return [
            Icon(
                src=f"data:image/png;base64,{b64}",
                mimeType="image/png",
                sizes=["512x512"],
            )
        ]
    return []
