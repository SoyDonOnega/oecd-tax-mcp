# taxmotion

Agent skill `/taxmotion`: animated explainer of a tax term, sourced through the OECD Tax MCP. Ships with `oecd-tax-mcp`.

## What it does

Creates an explainer motion of a tax term (animated 1920x1080 HTML, 45 to 75 seconds) in the style of the *GloBE in Five Steps* / *Tax Control Frameworks* series, with this MCP as the source. The motion is written in the language the user writes in. It covers the term → script → HTML workflow, the output-language rule, accuracy rules (OECD sources, mark what is illustrative), the house style, the full engine template and video export (Playwright capture or Remotion).

## Usage

```
/taxmotion DEMPE
```

Output: one self-contained HTML page, 1920x1080, with a player (play/pause, timeline, clock). Optional export to MP4.

From the MCP (nothing else to install), the `oecd-tax` server exposes:

- the `taxmotion` prompt (argument `term` and, optionally, `language`; without it, the motion follows the language of the conversation). In Claude Code it shows up as `/mcp__oecd-tax__taxmotion DEMPE`; in Claude Desktop, in the connector's prompt menu.
- the resources `skill://taxmotion/SKILL.md` and `skill://taxmotion/assets/tcf.html`.

## Install

Copy this folder as `<skills dir>/taxmotion/`, e.g. for Claude Code:

```bash
mkdir -p ~/.claude/skills && cp -R src/oecd_tax_mcp/skills/taxmotion ~/.claude/skills/
```

The skill is slash-only (`disable-model-invocation: true`): it runs on `/taxmotion`, not on its own.

## Requirements

The `oecd-tax` MCP server for sources. Video export only: Node with Playwright or Remotion.

## Layout

- `SKILL.md` — instructions and the HTML engine template.
- `assets/tcf.html` — reference motion (Tax Control Frameworks, in Spanish).
- `LICENSE` — MIT.

## License

MIT
