# STATUS — oecd-tax-mcp

**One-liner:** Local MCP for OECD tax soft-law PDFs + SDMX stats (Taxing Wages, ETR, …) with provenance and local derive.

**State:** done (MVP closed 2026-09-27)

## Links

- Vault: `Developer/Solutions/oecd-tax-mcp/`
- GitHub: https://github.com/SoyDonOnega/oecd-tax-mcp @ `3ab94e2` (private)
- Origin: not created (403 on `origin repo create`; GitHub tip is SoT for this slice)

## Proof

- Repo: https://github.com/SoyDonOnega/oecd-tax-mcp @ `3ab94e20bbb9fad326a88466c014521c6cbfac78`
- `cursor mcp list` → `oecd-tax: ready` (11 tools)
- Smoke: Taxing Wages ES 2024 tax wedge single 100% AW = **41.14%** labour costs (`DF_TW_COMP` / `AV_TW` / `S_C0` / `AW100`)

## Open

- None for MVP closeout

## Next

- Optional: pin GloBE Model Rules + TCF 2016 PDFs; Origin mirror when namespace allows; wire into `knowledge-sources`
