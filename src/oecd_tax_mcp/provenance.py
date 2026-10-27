"""Standard provenance envelopes for primary OECD pulls and derived figures."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


OECD_TERMS = (
    "Source: OECD. Reproduce with attribution. "
    "See OECD Terms and Conditions / SDMX API terms."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def primary_sdmx(
    *,
    flow_ref: str,
    request_url: str,
    key: str,
    start_period: str | None,
    end_period: str | None,
    dataset_name: str | None = None,
) -> dict[str, Any]:
    return {
        "kind": "primary",
        "publisher": "OECD",
        "channel": "SDMX REST",
        "api_base": request_url.split("/data/")[0] if "/data/" in request_url else None,
        "flow_ref": flow_ref,
        "dataset_name": dataset_name,
        "request_url": request_url,
        "query": {
            "key": key,
            "start_period": start_period,
            "end_period": end_period,
        },
        "retrieved_at": utc_now(),
        "cite": (
            f"OECD SDMX dataset {dataset_name or flow_ref} "
            f"(flow_ref={flow_ref}; key={key}; "
            f"period={start_period or '*'}–{end_period or '*'})."
        ),
        "terms": OECD_TERMS,
        "parents": [],
    }


def primary_pdf(
    *,
    instrument_id: str | None,
    title: str,
    pdf_url: str,
    doi: str | None = None,
    cite_as: str | None = None,
) -> dict[str, Any]:
    return {
        "kind": "primary",
        "publisher": "OECD",
        "channel": "OECD free PDF (/content/dam or /tax/beps)",
        "instrument_id": instrument_id,
        "title": title,
        "source_url": pdf_url,
        "doi": doi,
        "retrieved_at": utc_now(),
        "cite": cite_as or f"OECD — {title} ({pdf_url})",
        "terms": OECD_TERMS,
        "parents": [],
        "soft_law_note": "Organisation soft law / model instrument — not binding treaty law unless applicable as such.",
    }


def derived(
    *,
    operation: str,
    description: str,
    parents: list[dict[str, Any]],
    formula: str,
) -> dict[str, Any]:
    parent_cites = [p.get("cite") or p.get("flow_ref") or p.get("snapshot_id") for p in parents]
    return {
        "kind": "derived",
        "publisher": "oecd-tax-mcp (local derivation)",
        "channel": "computed_from_cached_primary",
        "operation": operation,
        "formula": formula,
        "description": description,
        "retrieved_at": utc_now(),
        "cite": (
            f"Derived locally via {operation}: {description}. "
            f"Based on OECD primary source(s): {'; '.join(str(c) for c in parent_cites if c)}."
        ),
        "terms": (
            "Derived figure is not published by OECD as such. "
            "Underlying observations remain OECD data — " + OECD_TERMS
        ),
        "parents": parents,
    }


def attach_row_provenance(row: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["provenance"] = {
        "kind": provenance.get("kind"),
        "flow_ref": provenance.get("flow_ref"),
        "request_url": provenance.get("request_url"),
        "retrieved_at": provenance.get("retrieved_at"),
        "cite": provenance.get("cite"),
        "source": "OECD",
    }
    return out
