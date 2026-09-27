"""OECD SDMX 2.1 client — statistical dataflows (public, keyless)."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

BASE_URL = os.environ.get(
    "OECD_SDMX_BASE_URL", "https://sdmx.oecd.org/public/rest"
).rstrip("/")
CACHE_DIR = Path(
    os.environ.get("OECD_TAX_MCP_CACHE", Path.home() / ".cache" / "oecd-tax-mcp")
)
FLOWS_CACHE = CACHE_DIR / "sdmx_dataflows_stubs.json"
FLOWS_TTL_SEC = int(os.environ.get("OECD_SDMX_CATALOG_TTL", str(24 * 3600)))
USER_AGENT = "oecd-tax-mcp/0.1 (+local MCP; SDMX research use)"

STRUCTURE_ACCEPT = "application/vnd.sdmx.structure+json;charset=utf-8;version=2"
DATA_ACCEPT = "application/vnd.sdmx.data+json;charset=utf-8;version=2.0.0"


def _client() -> httpx.Client:
    return httpx.Client(
        follow_redirects=True,
        timeout=httpx.Timeout(90.0),
        headers={"User-Agent": USER_AGENT},
    )


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_dataflows(*, force: bool = False) -> list[dict[str, Any]]:
    _ensure_cache_dir()
    if (
        not force
        and FLOWS_CACHE.exists()
        and time.time() - FLOWS_CACHE.stat().st_mtime < FLOWS_TTL_SEC
    ):
        return json.loads(FLOWS_CACHE.read_text(encoding="utf-8"))
    url = f"{BASE_URL}/dataflow/all?detail=allstubs"
    with _client() as client:
        resp = client.get(url, headers={"Accept": STRUCTURE_ACCEPT})
        resp.raise_for_status()
        payload = resp.json()
    flows = (payload.get("data") or {}).get("dataflows") or []
    slim: list[dict[str, Any]] = []
    for f in flows:
        name = f.get("name") or (f.get("names") or {}).get("en") or f.get("id")
        desc = f.get("description") or ""
        if isinstance(desc, dict):
            desc = desc.get("en") or ""
        slim.append(
            {
                "agency_id": f.get("agencyID"),
                "id": f.get("id"),
                "version": f.get("version"),
                "name": name,
                "description": (desc or "")[:400],
                "flow_ref": f"{f.get('agencyID')},{f.get('id')},{f.get('version')}",
            }
        )
    FLOWS_CACHE.write_text(json.dumps(slim), encoding="utf-8")
    return slim


def list_agencies() -> list[dict[str, Any]]:
    flows = fetch_dataflows()
    counts: dict[str, int] = {}
    for f in flows:
        aid = f.get("agency_id") or "UNKNOWN"
        counts[aid] = counts.get(aid, 0) + 1
    # Light labels for tax-relevant agencies
    labels = {
        "OECD.CTP.TPS": "Centre for Tax Policy and Statistics (tax stats, CbCR, ETR, …)",
        "OECD.CTP.TAV": "Centre for Tax Policy — Tax Administration / technology",
        "OECD.CFE.RDG": "Centre for Entrepreneurship — regional/subnational finance",
        "OECD.SDD.NAD": "Statistics and Data — National Accounts",
        "OECD.SDD.TPS": "Statistics and Data — prices / related",
    }
    rows = [
        {
            "agency_id": aid,
            "dataflow_count": n,
            "label": labels.get(aid),
            "tax_relevant": aid.startswith("OECD.CTP") or "TAX" in aid,
        }
        for aid, n in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return rows


def search_datasets(
    query: str,
    *,
    agency_id: str | None = None,
    tax_focus: bool = False,
    limit: int = 20,
) -> list[dict[str, Any]]:
    flows = fetch_dataflows()
    q = (query or "").strip().lower()
    tokens = [t for t in re.split(r"\s+", q) if t]
    scored: list[tuple[int, dict[str, Any]]] = []
    for f in flows:
        if agency_id and f.get("agency_id") != agency_id:
            continue
        if tax_focus and not (
            (f.get("agency_id") or "").startswith("OECD.CTP")
            or any(
                k in (f.get("name") or "").lower()
                or k in (f.get("description") or "").lower()
                or k in (f.get("id") or "").lower()
                for k in ("tax", "cbcr", "etr", "vat", "revenue", "withholding")
            )
        ):
            continue
        hay = " ".join(
            [
                f.get("agency_id") or "",
                f.get("id") or "",
                f.get("name") or "",
                f.get("description") or "",
            ]
        ).lower()
        if not tokens:
            score = 1
        else:
            score = 0
            if q and q in hay:
                score += 10
            for t in tokens:
                if t in hay:
                    score += 3
        if score:
            scored.append((score, f))
    scored.sort(key=lambda x: (-x[0], x[1].get("agency_id") or "", x[1].get("id") or ""))
    return [f for _, f in scored[: max(1, min(limit, 100))]]


def parse_flow_ref(flow_ref: str) -> tuple[str, str, str | None]:
    parts = [p.strip() for p in flow_ref.split(",")]
    if len(parts) < 2:
        raise ValueError(
            "flow_ref must look like 'OECD.CTP.TPS,DSD_ETR@DF_ETR_BASELINE,2.1'"
        )
    agency, df_id = parts[0], parts[1]
    version = parts[2] if len(parts) > 2 and parts[2] else None
    return agency, df_id, version


def get_dataflow(flow_ref: str) -> dict[str, Any]:
    agency, df_id, version = parse_flow_ref(flow_ref)
    ver = version or "latest"
    url = f"{BASE_URL}/dataflow/{agency}/{df_id}/{ver}"
    with _client() as client:
        resp = client.get(url, headers={"Accept": STRUCTURE_ACCEPT})
        resp.raise_for_status()
        payload = resp.json()
    flows = (payload.get("data") or {}).get("dataflows") or []
    if not flows:
        raise ValueError(f"No dataflow for {flow_ref}")
    f = flows[0]
    name = f.get("name") or (f.get("names") or {}).get("en") or df_id
    # structure link if present
    structure_ref = None
    for link in f.get("structure") and [f.get("structure")] or []:
        structure_ref = link
    # also check links
    for link in f.get("links") or []:
        if link.get("rel") in {"structure", "datastructure"}:
            structure_ref = link.get("urn") or link.get("href") or structure_ref
    return {
        "flow_ref": f"{f.get('agencyID')},{f.get('id')},{f.get('version')}",
        "agency_id": f.get("agencyID"),
        "id": f.get("id"),
        "version": f.get("version"),
        "name": name,
        "description": f.get("description")
        if isinstance(f.get("description"), str)
        else (f.get("description") or {}).get("en"),
        "structure_ref": structure_ref,
        "source": "OECD SDMX",
        "api": BASE_URL,
    }


def query_dataset(
    flow_ref: str,
    *,
    key: str = "all",
    start_period: str | None = None,
    end_period: str | None = None,
    max_rows: int = 50,
    store_all_rows: bool = True,
) -> dict[str, Any]:
    agency, df_id, version = parse_flow_ref(flow_ref)
    ver = version or "latest"
    flow = f"{agency},{df_id},{ver}"
    params: dict[str, str] = {"dimensionAtObservation": "AllDimensions"}
    if start_period:
        params["startPeriod"] = start_period
    if end_period:
        params["endPeriod"] = end_period
    url = f"{BASE_URL}/data/{flow}/{key or 'all'}"
    with _client() as client:
        resp = client.get(url, params=params, headers={"Accept": DATA_ACCEPT})
        if resp.status_code >= 400:
            raise ValueError(
                f"SDMX data query failed HTTP {resp.status_code}: {resp.text[:300]}"
            )
        payload = resp.json()
        final_url = str(resp.url)

    # Decode full response for snapshot chain; truncate only the agent-facing preview
    decode_cap = 50_000 if store_all_rows else max_rows
    all_rows, dim_ids, total = _decode_observations(payload, max_rows=decode_cap)
    preview = all_rows[: max(1, min(max_rows, 200))]
    return {
        "flow_ref": flow,
        "key": key,
        "start_period": start_period,
        "end_period": end_period,
        "dimension_ids": dim_ids,
        "request_url": final_url,
        "row_count_returned": len(preview),
        "row_count_total_in_response": total,
        "row_count_stored": len(all_rows),
        "truncated": total > len(preview),
        "rows": preview,
        "all_rows": all_rows if store_all_rows else preview,
        "source": "OECD",
        "hint": (
            "Primary OECD observations. For non-OECD inputs (e.g. national population), "
            "the agent must supply external_inputs to oecd_stats_derive — this MCP does not fetch them. "
            "Key example: ESP........ with start_period/end_period."
        ),
    }


def _decode_observations(
    payload: dict[str, Any], *, max_rows: int
) -> tuple[list[dict[str, Any]], list[str], int]:
    data = payload.get("data") or {}
    structures = data.get("structures") or []
    if not structures:
        return [], [], 0
    dims = (structures[0].get("dimensions") or {}).get("observation") or []
    dim_ids = [d.get("id") for d in dims]
    datasets = data.get("dataSets") or []
    if not datasets:
        return [], dim_ids, 0
    obs = datasets[0].get("observations") or {}
    total = len(obs)
    rows: list[dict[str, Any]] = []
    for i, (k, vals) in enumerate(obs.items()):
        if i >= max_rows:
            break
        idxs = [int(x) for x in k.split(":")]
        row: dict[str, Any] = {}
        for di, idx in enumerate(idxs):
            if di >= len(dims):
                break
            dim = dims[di]
            values = dim.get("values") or []
            if 0 <= idx < len(values):
                v = values[idx]
                row[dim["id"]] = {"id": v.get("id"), "name": v.get("name")}
            else:
                row[dim["id"]] = {"index": idx}
        row["value"] = vals[0] if vals else None
        if len(vals) > 1:
            row["obs_attributes"] = vals[1:]
        row["source"] = "OECD"
        rows.append(row)
    return rows, dim_ids, total
