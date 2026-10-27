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
gh repo clone SoyDonOnega/oecd-tax-mcp ~/src/oecd-tax-mcp
cd ~/src/oecd-tax-mcp && uv sync
```

## Register in Claude Code

User scope (every session):

```bash
claude mcp add-json -s user oecd-tax '{"type":"stdio","command":"uv","args":["--directory","/Users/One/src/oecd-tax-mcp","run","oecd-tax-mcp"]}'
```

Any other MCP client: same command (`uv --directory <clone> run oecd-tax-mcp`) as a stdio server.

Optional env:

- `OECD_TAX_MCP_CACHE` — PDF cache directory (default `~/.cache/oecd-tax-mcp`)

## Usage pattern

1. `oecd_tax_search("DEMPE")` or `oecd_tax_resolve("oecd:tpg-2022")`
2. `oecd_tax_get("oecd:tpg-2022", query="6.32")` or paginate with `page` / `max_chars`
3. Cite with `cite_as` + pinpoint; keep soft-law classification (guideline / model instrument)

## Skill: taxmotion

Turns a tax term into an animated HTML explainer (1920x1080) sourced through this MCP, in the language the user writes in. It ships inside the package and the server exposes it as:

- the MCP prompt `taxmotion` (`term`, optional `language`); in Claude Code: `/mcp__oecd-tax__taxmotion DEMPE`;
- the resources `skill://taxmotion/SKILL.md` and `skill://taxmotion/examples/tcf.html`.

To have it trigger on its own in Claude Code, also copy it as a skill: `cp -R src/oecd_tax_mcp/skills/taxmotion ~/.claude/skills/`. Details in `src/oecd_tax_mcp/skills/taxmotion/README.md`.

## Logo

Server icon: `assets/logo.png` (also packaged under `src/oecd_tax_mcp/assets/`). Exposed via MCP `serverInfo.icons` (PNG data URI). Some clients show a letter fallback; MCP Inspector renders it.

Code: MIT. OECD publications remain under OECD terms — attribute the source; do not republish wholesale. Read-only local cache for agent use.

## Status

See `STATUS.md` / `ROADMAP.md`.
