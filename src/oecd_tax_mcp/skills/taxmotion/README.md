# taxmotion

Skill that creates explainer motions of tax terms (animated 1920x1080 HTML) in the style of the *GloBE in Five Steps* / *Tax Control Frameworks* series, with this MCP as the source. The motion is written in the language the user writes in.

- `SKILL.md`: term → script → HTML workflow, output-language rule, accuracy rules (OECD sources, mark what is illustrative), style, full engine template and video export (Playwright capture or Remotion).
- `examples/tcf.html`: reference motion (Tax Control Frameworks, in Spanish).

## How to use it

**From the MCP (nothing else to install).** The `oecd-tax` server exposes:

- the `taxmotion` prompt (argument `term` and, optionally, `language`; without it, the motion follows the language of the conversation). In Claude Code it shows up as `/mcp__oecd-tax__taxmotion DEMPE`; in Claude Desktop, in the connector's prompt menu.
- the resources `skill://taxmotion/SKILL.md` and `skill://taxmotion/examples/tcf.html`.

**As a Claude Code skill** (so it triggers by itself when you ask "make me a motion about…"):

```bash
mkdir -p ~/.claude/skills && cp -R src/oecd_tax_mcp/skills/taxmotion ~/.claude/skills/
```

Then `/taxmotion DEMPE`.
