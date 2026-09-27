"""Derive new figures from cached OECD snapshots (+ optional agent-supplied official inputs).

Non-OECD series (INE population, Eurostat, AEAT aggregates, …) are NEVER fetched here.
The calling agent must pass them as external_inputs with cite + source_url.
"""

from __future__ import annotations

from typing import Any

from oecd_tax_mcp import provenance as prov
from oecd_tax_mcp.store import load_snapshot, save_snapshot


def _dim_id(cell: Any) -> str | None:
    if cell is None:
        return None
    if isinstance(cell, dict):
        return cell.get("id")
    return str(cell)


def _num(row: dict[str, Any]) -> float | None:
    v = row.get("value")
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _group_key(row: dict[str, Any], *, exclude: set[str]) -> tuple[str, ...]:
    parts: list[str] = []
    for k, v in sorted(row.items()):
        if k in exclude or k in {"value", "provenance", "obs_attributes", "source"}:
            continue
        if isinstance(v, dict) and "id" in v:
            parts.append(f"{k}={v.get('id')}")
        elif not isinstance(v, (dict, list)):
            parts.append(f"{k}={v}")
    return tuple(parts)


def _normalize_external(inputs: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Require provenance fields on every external official input."""
    if not inputs:
        return []
    out: list[dict[str, Any]] = []
    for raw in inputs:
        if not isinstance(raw, dict):
            raise ValueError("each external_input must be an object")
        for req in ("id", "value", "cite"):
            if req not in raw or raw[req] in (None, ""):
                raise ValueError(
                    f"external_input missing required field {req!r}. "
                    "Example: {id:'population_ESP_2021', value:47398383, "
                    "unit:'persons', cite:'INE Padrón 2021', source_url:'https://…'}"
                )
        try:
            value = float(raw["value"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"external_input {raw.get('id')!r} value must be numeric") from exc
        out.append(
            {
                "id": str(raw["id"]),
                "value": value,
                "unit": raw.get("unit"),
                "cite": str(raw["cite"]),
                "source_url": raw.get("source_url"),
                "publisher": raw.get("publisher"),
                "as_of": raw.get("as_of"),
                "match": raw.get("match") or {},  # e.g. {"REF_AREA": "ESP", "TIME_PERIOD": "2021"}
                "kind": "external_official",
                "note": "Not retrieved by oecd-tax-mcp; supplied by the agent from an official source.",
            }
        )
    return out


def derive(
    snapshot_id: str,
    operation: str,
    *,
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
    max_rows: int = 50,
) -> dict[str, Any]:
    snap = load_snapshot(snapshot_id)
    rows: list[dict[str, Any]] = list(snap.get("all_rows") or snap.get("rows") or [])
    if filter_dim and filter_value:
        rows = [r for r in rows if _dim_id(r.get(filter_dim)) == filter_value]

    externals = _normalize_external(external_inputs)
    parent_meta = {
        "snapshot_id": snapshot_id,
        "flow_ref": snap.get("flow_ref"),
        "cite": (snap.get("provenance") or {}).get("cite"),
        "request_url": (snap.get("provenance") or {}).get("request_url"),
        "retrieved_at": (snap.get("provenance") or {}).get("retrieved_at"),
        "kind": "primary_oecd",
    }

    op = operation.strip().lower()
    if op in {"yoy", "yoy_delta", "pct_change"}:
        derived_rows, formula, desc = _yoy(rows, group_by=group_by)
    elif op in {"compare", "diff"}:
        if not compare_a or not compare_b:
            raise ValueError("compare requires compare_a and compare_b (e.g. ESP and FRA)")
        derived_rows, formula, desc = _compare(
            rows, dim=compare_dim, a=compare_a, b=compare_b, group_by=group_by
        )
    elif op == "ratio":
        if not numerator_measure or not denominator_measure:
            raise ValueError("ratio requires numerator_measure and denominator_measure ids")
        derived_rows, formula, desc = _ratio(
            rows,
            numerator=numerator_measure,
            denominator=denominator_measure,
            group_by=group_by,
        )
    elif op in {"rank", "ranking"}:
        derived_rows, formula, desc = _rank(rows, group_by=group_by or ["TIME_PERIOD"])
    elif op in {"summary", "aggregate"}:
        derived_rows, formula, desc = _summary(rows, group_by=group_by)
    elif op in {"per_external", "divide_by_external", "per_capita"}:
        if not externals:
            raise ValueError(
                "per_external requires external_inputs supplied by the agent "
                "(e.g. official population). This MCP does not fetch INE/Eurostat/etc."
            )
        ext = _pick_external(externals, external_id)
        derived_rows, formula, desc = _per_external(rows, external=ext)
    else:
        raise ValueError(
            f"Unknown operation {operation!r}. "
            "Use: yoy | compare | ratio | rank | summary | per_external"
        )

    parents: list[dict[str, Any]] = [parent_meta]
    for e in externals:
        parents.append(
            {
                "kind": "external_official",
                "id": e["id"],
                "cite": e["cite"],
                "source_url": e.get("source_url"),
                "publisher": e.get("publisher"),
                "value": e["value"],
                "unit": e.get("unit"),
            }
        )

    provenance = prov.derived(
        operation=op,
        description=desc,
        parents=parents,
        formula=formula,
    )
    capped = derived_rows[: max(1, min(max_rows, 200))]
    for r in capped:
        r["provenance"] = {
            "kind": "derived",
            "operation": op,
            "formula": formula,
            "parent_snapshot_id": snapshot_id,
            "parent_flow_ref": snap.get("flow_ref"),
            "parent_cite": parent_meta.get("cite"),
            "external_inputs_used": [
                {"id": e["id"], "cite": e["cite"], "source_url": e.get("source_url")}
                for e in externals
            ],
            "cite": provenance["cite"],
            "source": "derived_from_OECD_plus_external"
            if externals
            else "derived_from_OECD",
        }

    out = {
        "ok": True,
        "operation": op,
        "formula": formula,
        "description": desc,
        "parent_snapshot_id": snapshot_id,
        "external_inputs": externals,
        "row_count_returned": len(capped),
        "row_count_total": len(derived_rows),
        "truncated": len(derived_rows) > len(capped),
        "rows": capped,
        "provenance": provenance,
        "boundary": (
            "oecd-tax-mcp fetches OECD only. Other official series must be passed "
            "as external_inputs with cite/source_url by the agent (not via this MCP)."
        ),
    }
    out["snapshot_id"] = save_snapshot(
        {
            "kind": "derived",
            "operation": op,
            "flow_ref": snap.get("flow_ref"),
            "parent_snapshot_id": snapshot_id,
            "external_inputs": externals,
            "all_rows": derived_rows,
            "rows": capped,
            "provenance": provenance,
        }
    )
    return out


def _pick_external(externals: list[dict[str, Any]], external_id: str | None) -> dict[str, Any]:
    if external_id:
        for e in externals:
            if e["id"] == external_id:
                return e
        raise ValueError(f"external_id {external_id!r} not found in external_inputs")
    if len(externals) != 1:
        raise ValueError("pass external_id when more than one external_input is provided")
    return externals[0]


def _per_external(
    rows: list[dict[str, Any]], *, external: dict[str, Any]
) -> tuple[list[dict[str, Any]], str, str]:
    """Divide each OECD observation by an agent-supplied official scalar (e.g. population)."""
    denom = float(external["value"])
    if denom == 0:
        raise ValueError("external_input value must be non-zero")
    match = external.get("match") or {}
    out: list[dict[str, Any]] = []
    for r in rows:
        if match:
            ok = True
            for dim, want in match.items():
                if _dim_id(r.get(dim)) != str(want):
                    ok = False
                    break
            if not ok:
                continue
        val = _num(r)
        if val is None:
            continue
        row = dict(r)
        row["value_oecd"] = val
        row["external_id"] = external["id"]
        row["external_value"] = denom
        row["external_unit"] = external.get("unit")
        row["external_cite"] = external["cite"]
        row["value"] = val / denom
        out.append(row)
    formula = f"oecd_value / external[{external['id']}]"
    desc = (
        f"OECD observation divided by agent-supplied official input "
        f"{external['id']} ({external['cite']})"
    )
    return out, formula, desc


def _yoy(
    rows: list[dict[str, Any]], *, group_by: list[str] | None
) -> tuple[list[dict[str, Any]], str, str]:
    exclude = {"TIME_PERIOD", "value", "provenance", "obs_attributes", "source"}
    # optional extra group dims already in key via exclude TIME only
    by_series: dict[tuple[str, ...], dict[str, float]] = {}
    meta: dict[tuple[str, ...], dict[str, Any]] = {}
    for r in rows:
        period = _dim_id(r.get("TIME_PERIOD"))
        val = _num(r)
        if period is None or val is None:
            continue
        key = _group_key(r, exclude=exclude)
        by_series.setdefault(key, {})[period] = val
        meta[key] = {k: v for k, v in r.items() if k not in {"value", "TIME_PERIOD", "provenance"}}

    out: list[dict[str, Any]] = []
    for key, series in by_series.items():
        periods = sorted(series.keys())
        for i in range(1, len(periods)):
            prev_p, cur_p = periods[i - 1], periods[i]
            prev_v, cur_v = series[prev_p], series[cur_p]
            if prev_v == 0:
                continue
            delta = cur_v - prev_v
            pct = (delta / prev_v) * 100.0
            row = dict(meta.get(key) or {})
            row.update(
                {
                    "TIME_PERIOD": {"id": cur_p, "name": cur_p},
                    "prior_period": prev_p,
                    "value_prior": prev_v,
                    "value": cur_v,
                    "delta": delta,
                    "pct_change": pct,
                    "unit_note": "pct_change is percent, not percentage points unless series is already a rate",
                }
            )
            out.append(row)
    formula = "(value_t - value_{t-1}) / value_{t-1} * 100"
    desc = "Year-on-year (period-on-period) percent change within each dimension series"
    return out, formula, desc


def _compare(
    rows: list[dict[str, Any]],
    *,
    dim: str,
    a: str,
    b: str,
    group_by: list[str] | None,
) -> tuple[list[dict[str, Any]], str, str]:
    exclude = {dim, "value", "provenance", "obs_attributes", "source"}
    buckets: dict[tuple[str, ...], dict[str, float]] = {}
    meta: dict[tuple[str, ...], dict[str, Any]] = {}
    for r in rows:
        code = _dim_id(r.get(dim))
        val = _num(r)
        if code not in {a, b} or val is None:
            continue
        key = _group_key(r, exclude=exclude)
        buckets.setdefault(key, {})[code] = val
        meta[key] = {k: v for k, v in r.items() if k not in {dim, "value", "provenance"}}

    out: list[dict[str, Any]] = []
    for key, pair in buckets.items():
        if a not in pair or b not in pair:
            continue
        row = dict(meta.get(key) or {})
        row.update(
            {
                "compare_dim": dim,
                "compare_a": a,
                "compare_b": b,
                f"value_{a}": pair[a],
                f"value_{b}": pair[b],
                "delta_a_minus_b": pair[a] - pair[b],
                "value": pair[a] - pair[b],
            }
        )
        out.append(row)
    formula = f"value({dim}={a}) - value({dim}={b})"
    desc = f"Difference between {dim}={a} and {dim}={b} on matching remaining dimensions"
    return out, formula, desc


def _ratio(
    rows: list[dict[str, Any]],
    *,
    numerator: str,
    denominator: str,
    group_by: list[str] | None,
) -> tuple[list[dict[str, Any]], str, str]:
    exclude = {"MEASURE", "value", "provenance", "obs_attributes", "source"}
    buckets: dict[tuple[str, ...], dict[str, float]] = {}
    meta: dict[tuple[str, ...], dict[str, Any]] = {}
    for r in rows:
        m = _dim_id(r.get("MEASURE"))
        val = _num(r)
        if m not in {numerator, denominator} or val is None:
            continue
        key = _group_key(r, exclude=exclude)
        buckets.setdefault(key, {})[m] = val
        meta[key] = {k: v for k, v in r.items() if k not in {"MEASURE", "value", "provenance"}}

    out: list[dict[str, Any]] = []
    for key, pair in buckets.items():
        if numerator not in pair or denominator not in pair or pair[denominator] == 0:
            continue
        row = dict(meta.get(key) or {})
        ratio = pair[numerator] / pair[denominator]
        row.update(
            {
                "numerator_measure": numerator,
                "denominator_measure": denominator,
                "value_numerator": pair[numerator],
                "value_denominator": pair[denominator],
                "value": ratio,
            }
        )
        out.append(row)
    formula = f"MEASURE[{numerator}] / MEASURE[{denominator}]"
    desc = f"Ratio of measure {numerator} to {denominator} on matching dimensions"
    return out, formula, desc


def _rank(
    rows: list[dict[str, Any]], *, group_by: list[str]
) -> tuple[list[dict[str, Any]], str, str]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for r in rows:
        if _num(r) is None:
            continue
        key = tuple(_dim_id(r.get(g)) or "" for g in group_by)
        groups.setdefault(key, []).append(r)

    out: list[dict[str, Any]] = []
    for key, items in groups.items():
        ordered = sorted(items, key=lambda r: _num(r) or float("-inf"), reverse=True)
        for i, r in enumerate(ordered, start=1):
            row = dict(r)
            row["rank"] = i
            row["rank_group"] = dict(zip(group_by, key))
            out.append(row)
    formula = f"rank(value DESC) within group_by={group_by}"
    desc = f"Rank observations by value descending within {group_by}"
    return out, formula, desc


def _summary(
    rows: list[dict[str, Any]], *, group_by: list[str] | None
) -> tuple[list[dict[str, Any]], str, str]:
    groups: dict[tuple[str, ...], list[float]] = {}
    for r in rows:
        val = _num(r)
        if val is None:
            continue
        if group_by:
            key = tuple(_dim_id(r.get(g)) or "" for g in group_by)
        else:
            key = ("__all__",)
        groups.setdefault(key, []).append(val)

    out: list[dict[str, Any]] = []
    for key, vals in groups.items():
        vals_sorted = sorted(vals)
        n = len(vals_sorted)
        mid = n // 2
        median = (
            vals_sorted[mid]
            if n % 2 == 1
            else (vals_sorted[mid - 1] + vals_sorted[mid]) / 2
        )
        row: dict[str, Any] = {
            "n": n,
            "min": vals_sorted[0],
            "max": vals_sorted[-1],
            "mean": sum(vals_sorted) / n,
            "median": median,
            "value": sum(vals_sorted) / n,
        }
        if group_by:
            row["group"] = dict(zip(group_by, key))
        out.append(row)
    formula = "n, min, max, mean, median of value"
    desc = f"Summary stats grouped by {group_by or 'all rows'}"
    return out, formula, desc
