# ROADMAP — oecd-tax-mcp

## Done (MVP 0.2)

- Soft-law PDF lane + SDMX stats lane
- Provenance on primary rows; snapshots; derive (yoy/compare/ratio/rank/summary/per_external)
- External official inputs (INE etc.) only via agent-supplied `external_inputs` — not fetched by this MCP
- Logo in `assets/logo.png` → MCP `icons`
- Cursor `~/.cursor/mcp.json` entry `oecd-tax`

## Later (optional)

1. Pin missing free PDFs: GloBE Model Rules (2021), TCF 2016 *Building Better Tax Control Frameworks*
2. SDMX dimension-values helper / safer key builder
3. Wire into `knowledge-sources` citation audit
4. Origin `onega/oecd-tax-mcp` if José wants Origin as coding SoT
5. Cursor plugin packaging only if logo visibility in UI becomes a requirement
