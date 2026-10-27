"""OECD tax MCP — soft-law PDFs + SDMX statistics + provenance-aware derivation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from oecd_tax_mcp import derive as derive_mod
from oecd_tax_mcp import provenance as prov
from oecd_tax_mcp import sdmx
from oecd_tax_mcp.catalog import (
    dataset_note,
    instruments,
    public_meta,
    resolve_instrument,
    search_instruments,
)
from oecd_tax_mcp.fetch import (
    cache_dir,
    extract_text,
    fetch_pdf,
    find_snippets,
    is_oecd_url,
    paginate,
    pdf_title,
)
from oecd_tax_mcp.icons import server_icons
from oecd_tax_mcp.store import list_snapshots, load_snapshot, save_snapshot

mcp = FastMCP(
    "OECD Tax",
    icons=server_icons() or None,
    instructions=(
        "OECD MCP — two lanes + derivation:\n"
        "1) Soft-law docs: oecd_tax_search/resolve/get (curated free PDFs). Soft law ≠ treaty.\n"
        "   Any other OECD PDF: oecd_tax_fetch(url) — direct PDF URL on oecd.org "
        "(usually /content/dam/…). Find the URL first (e.g. web search); DOI and HTML "
        "pages are Cloudflare-blocked.\n"
        "2) Statistics: oecd_stats_* via public SDMX (tax hub OECD.CTP.TPS).\n"
        "3) Derive: oecd_stats_derive from saved snapshots (yoy/compare/ratio/rank/summary/"
        "per_external). Every row carries provenance.\n"
        "BOUNDARY: this MCP fetches OECD only. Other official inputs (INE population, "
        "Eurostat, AEAT, …) must be supplied by the agent as external_inputs with cite + "
        "source_url — never invent them and never expect this MCP to download them.\n"
        "Always distinguish primary OECD vs derived vs external_official in citations.\n"
        "Skill: the `taxmotion` prompt (and skill://taxmotion/* resources) turns a tax term "
        "into an animated HTML explainer sourced through this MCP."
    ),
)


def _ok(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.tool()
def oecd_tax_health() -> str:
    """Report soft-law catalogue, SDMX cache, snapshots, and boundary notes."""
    try:
        n_flows = len(sdmx.fetch_dataflows())
        sdmx_ok = True
        sdmx_err = None
    except Exception as exc:  # noqa: BLE001
        n_flows = 0
        sdmx_ok = False
        sdmx_err = str(exc)
    snaps = list_snapshots(limit=5)
    return _ok(
        {
            "ok": True,
            "soft_law_instruments": len(instruments()),
            "sdmx_dataflows_cached": n_flows,
            "sdmx_ok": sdmx_ok,
            "sdmx_error": sdmx_err,
            "recent_snapshots": snaps,
            "cache_dir": str(cache_dir()),
            "dataset_note": dataset_note(),
            "boundary": (
                "Fetches OECD only. Non-OECD official series → agent external_inputs "
                "to oecd_stats_derive (not via this MCP)."
            ),
            "lanes": {
                "docs": [
                    "oecd_tax_list",
                    "oecd_tax_search",
                    "oecd_tax_resolve",
                    "oecd_tax_get",
                    "oecd_tax_fetch",
                ],
                "stats": [
                    "oecd_stats_agencies",
                    "oecd_stats_search",
                    "oecd_stats_dataflow",
                    "oecd_stats_query",
                    "oecd_stats_snapshots",
                    "oecd_stats_derive",
                ],
            },
        }
    )


@mcp.tool()
def oecd_tax_list(limit: int = 50) -> str:
    """List curated OECD tax soft-law instruments in the local catalogue."""
    rows = [public_meta(i) for i in instruments()[: max(1, min(limit, 100))]]
    return _ok(
        {
            "count": len(rows),
            "instruments": rows,
            "dataset_note": dataset_note(),
            "provenance": {
                "kind": "catalogue",
                "publisher": "oecd-tax-mcp curated catalogue",
                "note": "IDs/URLs curated locally; document text comes from OECD PDFs on get.",
            },
        }
    )


@mcp.tool()
def oecd_tax_search(query: str, limit: int = 10) -> str:
    """Search the soft-law catalogue by title, alias, topic, or id (not SDMX)."""
    hits = search_instruments(query, limit=max(1, min(limit, 25)))
    return _ok(
        {
            "query": query,
            "count": len(hits),
            "results": [public_meta(h) for h in hits],
            "dataset_note": dataset_note(),
            "hint": "Docs only. For statistics use oecd_stats_search.",
        }
    )


@mcp.tool()
def oecd_tax_resolve(identifier: str) -> str:
    """Resolve an instrument id, alias, or DOI to catalogue metadata + canonical PDF URL."""
    inst = resolve_instrument(identifier)
    if not inst:
        return _ok(
            {
                "verified": False,
                "identifier": identifier,
                "error": "not_found",
                "hint": "Try oecd_tax_search. Example ids: oecd:tpg-2022, oecd:mtc-2017-condensed",
                "dataset_note": dataset_note(),
            }
        )
    meta = public_meta(inst)
    meta["verified"] = True
    meta["provenance"] = {
        "kind": "catalogue_resolve",
        "publisher": "oecd-tax-mcp",
        "pdf_url": inst.get("pdf_url"),
        "doi": inst.get("doi"),
        "cite": inst.get("cite_as"),
    }
    return _ok(meta)


@mcp.tool()
def oecd_tax_get(
    identifier: str,
    query: str | None = None,
    max_chars: int = 12000,
    page: int = 1,
    force_download: bool = False,
) -> str:
    """Download (cached) a soft-law PDF and return extracted text with provenance."""
    inst = resolve_instrument(identifier)
    if not inst:
        return _ok(
            {
                "verified": False,
                "identifier": identifier,
                "error": "not_found",
                "dataset_note": dataset_note(),
            }
        )
    pdf_url = inst.get("pdf_url")
    if not pdf_url:
        return _ok(
            {
                "verified": False,
                "id": inst["id"],
                "error": "no_pdf_url",
                "landing_url": inst.get("landing_url"),
                "dataset_note": dataset_note(),
            }
        )
    try:
        path = fetch_pdf(pdf_url, force=force_download)
        text = extract_text(path)
    except Exception as exc:  # noqa: BLE001
        return _ok(
            {
                "verified": False,
                "id": inst["id"],
                "pdf_url": pdf_url,
                "error": "fetch_or_extract_failed",
                "detail": str(exc),
                "dataset_note": dataset_note(),
            }
        )

    provenance = prov.primary_pdf(
        instrument_id=inst["id"],
        title=inst["title"],
        pdf_url=pdf_url,
        doi=inst.get("doi"),
        cite_as=inst.get("cite_as"),
    )
    base = {
        "verified": True,
        "id": inst["id"],
        "title": inst["title"],
        "year": inst.get("year"),
        "authority": inst.get("authority"),
        "cite_as": inst.get("cite_as"),
        "source_url": pdf_url,
        "landing_url": inst.get("landing_url"),
        "doi": inst.get("doi"),
        "cached_pdf": str(path),
        "jurisdiction": "OECD/international",
        "dataset_note": dataset_note(),
        "provenance": provenance,
    }

    return _text_payload(base, text, query=query, max_chars=max_chars, page=page)


def _text_payload(
    base: dict[str, Any], text: str, *, query: str | None, max_chars: int, page: int
) -> str:
    if query:
        snippets = find_snippets(text, query)
        base.update(
            {
                "mode": "snippets",
                "query": query,
                "snippet_count": len(snippets),
                "snippets": snippets,
            }
        )
        return _ok(base)

    chunk, page_meta = paginate(text, max_chars=max_chars, page=page)
    base.update({"mode": "page", "text": chunk, **page_meta})
    return _ok(base)


@mcp.tool()
def oecd_tax_fetch(
    url: str,
    query: str | None = None,
    max_chars: int = 12000,
    page: int = 1,
    force_download: bool = False,
) -> str:
    """Download (cached) any OECD PDF by direct URL, outside the catalogue, with provenance.

    Only https PDFs on oecd.org (usually /content/dam/…). Find the URL first, e.g. with
    web search; DOI and HTML pages are Cloudflare-blocked. Same query/page modes as oecd_tax_get.
    """
    if not is_oecd_url(url):
        return _ok(
            {
                "verified": False,
                "url": url,
                "error": "not_oecd_url",
                "hint": "Only https PDF URLs on oecd.org. This MCP fetches OECD only.",
            }
        )
    try:
        path = fetch_pdf(url, force=force_download)
        title = pdf_title(path)
        text = extract_text(path)
    except Exception as exc:  # noqa: BLE001
        return _ok(
            {
                "verified": False,
                "url": url,
                "error": "fetch_or_extract_failed",
                "detail": str(exc),
            }
        )

    title = title or url.rsplit("/", 1)[-1]
    provenance = prov.primary_pdf(instrument_id=None, title=title, pdf_url=url)
    base = {
        "verified": True,
        "catalogued": False,
        "title": title,
        "title_source": "PDF metadata or file name — check against the document's cover",
        "cite_as": provenance["cite"],
        "source_url": url,
        "cached_pdf": str(path),
        "jurisdiction": "OECD/international",
        "provenance": provenance,
    }
    return _text_payload(base, text, query=query, max_chars=max_chars, page=page)


# --- SDMX statistics lane -------------------------------------------------


@mcp.tool()
def oecd_stats_agencies() -> str:
    """List SDMX agencies with dataflow counts (OECD.CTP.TPS = tax statistics hub)."""
    try:
        rows = sdmx.list_agencies()
    except Exception as exc:  # noqa: BLE001
        return _ok({"ok": False, "error": str(exc)})
    return _ok(
        {
            "count": len(rows),
            "agencies": rows[:40],
            "provenance": {
                "kind": "primary",
                "publisher": "OECD",
                "channel": "SDMX dataflow stubs",
                "api_base": sdmx.BASE_URL,
            },
            "hint": "Filter oecd_stats_search with agency_id='OECD.CTP.TPS' for corporate tax / CbCR / ETR.",
        }
    )


@mcp.tool()
def oecd_stats_search(
    query: str,
    agency_id: str | None = None,
    tax_focus: bool = True,
    limit: int = 20,
    refresh_catalog: bool = False,
) -> str:
    """Search OECD SDMX dataflows by keyword. Returns flow_ref for query/derive."""
    try:
        if refresh_catalog:
            sdmx.fetch_dataflows(force=True)
        hits = sdmx.search_datasets(
            query,
            agency_id=agency_id,
            tax_focus=tax_focus,
            limit=max(1, min(limit, 100)),
        )
    except Exception as exc:  # noqa: BLE001
        return _ok({"ok": False, "error": str(exc)})
    return _ok(
        {
            "query": query,
            "agency_id": agency_id,
            "tax_focus": tax_focus,
            "count": len(hits),
            "results": hits,
            "provenance": {
                "kind": "primary",
                "publisher": "OECD",
                "channel": "SDMX dataflow catalogue",
                "api_base": sdmx.BASE_URL,
            },
        }
    )


@mcp.tool()
def oecd_stats_dataflow(flow_ref: str) -> str:
    """Fetch metadata for one SDMX dataflow."""
    try:
        meta = sdmx.get_dataflow(flow_ref)
    except Exception as exc:  # noqa: BLE001
        return _ok({"ok": False, "flow_ref": flow_ref, "error": str(exc)})
    meta["ok"] = True
    meta["provenance"] = {
        "kind": "primary",
        "publisher": "OECD",
        "channel": "SDMX dataflow",
        "flow_ref": meta.get("flow_ref"),
        "api_base": sdmx.BASE_URL,
    }
    return _ok(meta)


@mcp.tool()
def oecd_stats_query(
    flow_ref: str,
    key: str = "all",
    start_period: str | None = None,
    end_period: str | None = None,
    max_rows: int = 40,
) -> str:
    """
    Query SDMX observations, attach provenance, and save a snapshot for derivation.

    Returns snapshot_id for oecd_stats_derive. Does not fetch non-OECD series.
    """
    try:
        result = sdmx.query_dataset(
            flow_ref,
            key=key,
            start_period=start_period,
            end_period=end_period,
            max_rows=max(1, min(max_rows, 200)),
            store_all_rows=True,
        )
    except Exception as exc:  # noqa: BLE001
        return _ok(
            {
                "ok": False,
                "flow_ref": flow_ref,
                "key": key,
                "error": str(exc),
            }
        )

    provenance = prov.primary_sdmx(
        flow_ref=result["flow_ref"],
        request_url=result.get("request_url") or "",
        key=key,
        start_period=start_period,
        end_period=end_period,
    )
    labeled = [prov.attach_row_provenance(r, provenance) for r in result["rows"]]
    all_labeled = [
        prov.attach_row_provenance(r, provenance) for r in result.get("all_rows") or result["rows"]
    ]
    snapshot_id = save_snapshot(
        {
            "kind": "primary",
            "flow_ref": result["flow_ref"],
            "key": key,
            "start_period": start_period,
            "end_period": end_period,
            "dimension_ids": result.get("dimension_ids"),
            "request_url": result.get("request_url"),
            "rows": labeled,
            "all_rows": all_labeled,
            "provenance": provenance,
        }
    )
    return _ok(
        {
            "ok": True,
            "snapshot_id": snapshot_id,
            "flow_ref": result["flow_ref"],
            "key": key,
            "start_period": start_period,
            "end_period": end_period,
            "dimension_ids": result.get("dimension_ids"),
            "row_count_returned": len(labeled),
            "row_count_stored": len(all_labeled),
            "row_count_total_in_response": result.get("row_count_total_in_response"),
            "truncated": result.get("truncated"),
            "rows": labeled,
            "provenance": provenance,
            "hint": (
                "Use snapshot_id with oecd_stats_derive. "
                "For population etc., pass external_inputs (cite+source_url) — not fetched here."
            ),
        }
    )


@mcp.tool()
def oecd_stats_snapshots(limit: int = 20) -> str:
    """List recent primary/derived snapshots saved under the local cache."""
    return _ok({"count": limit, "snapshots": list_snapshots(limit=limit)})


@mcp.tool()
def oecd_stats_derive(
    snapshot_id: str,
    operation: str,
    group_by: list[str] | None = None,
    filter_dim: str | None = None,
    filter_value: str | None = None,
    compare_dim: str = "REF_AREA",
    compare_a: str | None = None,
    compare_b: str | None = None,
    numerator_measure: str | None = None,
    denominator_measure: str | None = None,
    external_inputs: list[dict[str, Any]] | None = None,
    external_id: str | None = None,
    max_rows: int = 40,
) -> str:
    """
    Derive metrics from a saved OECD snapshot, with full provenance chain.

    Operations: yoy | compare | ratio | rank | summary | per_external

    per_external (alias per_capita): divide OECD values by an agent-supplied official
    scalar. external_inputs REQUIRED shape:
      {id, value, cite, source_url?, unit?, publisher?, as_of?, match?}
    Example population: {id:'pop_ESP_2021', value:47398383, unit:'persons',
      cite:'INE Padrón continuo 2021', source_url:'https://…', match:{REF_AREA:'ESP'}}

    This tool never downloads INE/Eurostat/AEAT — only uses what you pass.
    """
    try:
        # Ensure snapshot exists early for clearer errors
        load_snapshot(snapshot_id)
        result = derive_mod.derive(
            snapshot_id,
            operation,
            group_by=group_by,
            filter_dim=filter_dim,
            filter_value=filter_value,
            compare_dim=compare_dim,
            compare_a=compare_a,
            compare_b=compare_b,
            numerator_measure=numerator_measure,
            denominator_measure=denominator_measure,
            external_inputs=external_inputs,
            external_id=external_id,
            max_rows=max(1, min(max_rows, 200)),
        )
    except Exception as exc:  # noqa: BLE001
        return _ok(
            {
                "ok": False,
                "snapshot_id": snapshot_id,
                "operation": operation,
                "error": str(exc),
            }
        )
    return _ok(result)


_TAXMOTION = Path(__file__).parent / "skills" / "taxmotion"


@mcp.resource("skill://taxmotion/SKILL.md", mime_type="text/markdown")
def taxmotion_skill() -> str:
    """Taxmotion skill: workflow, accuracy rules, house style and HTML engine for tax-term motions."""
    return (_TAXMOTION / "SKILL.md").read_text(encoding="utf-8")


@mcp.resource("skill://taxmotion/assets/tcf.html", mime_type="text/html")
def taxmotion_example() -> str:
    """Reference motion of the series (Tax Control Frameworks, Spanish)."""
    return (_TAXMOTION / "assets" / "tcf.html").read_text(encoding="utf-8")


@mcp.prompt(name="taxmotion", description="Create an animated motion that explains a tax term")
def taxmotion_prompt(term: str, language: str = "") -> str:
    """Load the taxmotion skill and apply it to one tax term."""
    lang = (
        f"with the on-screen text in {language}"
        if language
        else "with the on-screen text in the language the user writes in"
    )
    return (
        f"Create a taxmotion motion about \"{term}\", {lang}. "
        "Follow these instructions exactly. Use this MCP's oecd_tax_* and oecd_stats_* "
        "tools as the source, and read the resource skill://taxmotion/assets/tcf.html "
        "as the pattern if your client allows it.\n\n"
        + taxmotion_skill()
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
