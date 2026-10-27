# taxmotion

Skill para crear motions explicativos de términos fiscales (HTML animado 1920x1080) con el estilo de la serie *GloBE in Five Steps* / *Tax Control Frameworks*, usando este MCP como fuente.

- `SKILL.md`: flujo término → guion → HTML, reglas de rigor (fuentes OCDE, marcar lo ilustrativo), estilo, plantilla completa del motor y exportación a vídeo (captura con Playwright o Remotion).
- `examples/tcf.html`: motion de referencia (Tax Control Frameworks, en español).

## Cómo se usa

**Desde el MCP (sin instalar nada más).** El servidor `oecd-tax` expone:

- el prompt `taxmotion` (argumentos `termino` y, opcional, `idioma`). En Claude Code aparece como `/mcp__oecd-tax__taxmotion DEMPE`; en Claude Desktop, en el menú de prompts del conector.
- los recursos `skill://taxmotion/SKILL.md` y `skill://taxmotion/examples/tcf.html`.

**Como skill de Claude Code** (para que se active sola cuando pidas "hazme un motion sobre…"):

```bash
mkdir -p ~/.claude/skills && cp -R src/oecd_tax_mcp/skills/taxmotion ~/.claude/skills/
```

Luego `/taxmotion DEMPE`.
