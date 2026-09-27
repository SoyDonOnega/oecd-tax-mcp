# oecd-tax-mcp

Local **Model Context Protocol** server for OECD **tax soft-law PDFs** and **SDMX statistics** (same server, two tool lanes).

- **Docs:** curated free PDFs (MTC, TPG, Pillar Two, co-operative compliance).
- **Stats:** public SDMX API (~1,500 dataflows; tax hub `OECD.CTP.TPS` — ETR, CbCR, carbon rates, …).

For heavy multi-country SQL spillover, `cyanheads/oecd-mcp-server` remains optional; this MCP keeps a simpler query + row cap.

## Why this shape

- `oecd.org` HTML hubs are often behind Cloudflare; agents cannot reliably WebFetch them.
- Free PDFs under `oecd.org/content/dam/...` (and some `/tax/beps/`) return HTTP 200 and are cacheable.
- Catalogue is explicit and versionable — no pretending there is a full-text OECD tax search API.

## Tools

| Tool | Role |
| --- | --- |
| `oecd_tax_health` | Soft-law + SDMX status |
| `oecd_tax_list` / `search` / `resolve` / `get` | Soft-law PDF lane |
| `oecd_stats_agencies` | SDMX agencies + counts |
| `oecd_stats_search` | Search dataflows (`tax_focus` default true) |
| `oecd_stats_dataflow` | Metadata for one `flow_ref` |
| `oecd_stats_query` | Observations (`key`, period, `max_rows`) |

## Install

```bash
cd "…/Developer/Solutions/oecd-tax-mcp"
uv sync
```

## Cursor MCP config

Add to your MCP settings (path adjust to your machine):

```json
{
  "mcpServers": {
    "oecd-tax": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/One/Library/CloudStorage/GoogleDrive-noonebutonega@gmail.com/My Drive/Obsidian/Developer/Solutions/oecd-tax-mcp",
        "run",
        "oecd-tax-mcp"
      ]
    }
  }
}
```

Optional env:

- `OECD_TAX_MCP_CACHE` — PDF cache directory (default `~/.cache/oecd-tax-mcp`)

## Usage pattern

1. `oecd_tax_search("DEMPE")` or `oecd_tax_resolve("oecd:tpg-2022")`
2. `oecd_tax_get("oecd:tpg-2022", query="6.32")` or paginate with `page` / `max_chars`
3. Cite with `cite_as` + pinpoint; keep soft-law classification (guideline / model instrument)

## Logo

Server icon: `assets/logo.png` (also packaged under `src/oecd_tax_mcp/assets/`). Exposed via MCP `serverInfo.icons` (PNG data URI). Cursor’s MCP list may still show a letter fallback — other clients / MCP Inspector can render it.

Code: MIT. OECD publications remain under OECD terms — attribute the source; do not republish wholesale. Read-only local cache for agent use.

## Status

See `STATUS.md` / `ROADMAP.md`.
