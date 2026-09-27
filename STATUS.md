# STATUS — oecd-tax-mcp

**One-liner:** Local MCP for OECD tax soft-law PDFs + SDMX stats (Taxing Wages, ETR, …) with provenance and local derive.

**State:** done (MVP closed 2026-09-27)

## Links

- Vault: `Developer/Solutions/oecd-tax-mcp/`
- GitHub: `SoyDonOnega/oecd-tax-mcp` (pending push if auth) 
- Origin: not created (GitHub-first for this slice)

## Proof

- `cursor mcp list` → `oecd-tax: ready` (11 tools)
- Smoke: Taxing Wages ES 2024 tax wedge single 100% AW = **41.14%** labour costs from `DF_TW_COMP` (`AV_TW`, `S_C0`, `AW100`)
- SDMX initialize includes `serverInfo.icons` (PNG logo); Cursor UI may not render custom icons

## Open

- None for MVP closeout

## Next

- Optional: pin GloBE Model Rules + TCF 2016 PDFs; Origin mirror if José wants coding SoT there; wire into `knowledge-sources` audit
