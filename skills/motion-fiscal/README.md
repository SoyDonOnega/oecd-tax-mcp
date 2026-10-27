# motion-fiscal

Skill de Claude para crear motions explicativos de términos fiscales (HTML animado 1920x1080) con el estilo de la serie *GloBE in Five Steps* / *Tax Control Frameworks*, usando este MCP como fuente.

- `SKILL.md`: flujo término → guion → HTML, reglas de rigor (fuentes OCDE, marcar lo ilustrativo), estilo, plantilla completa del motor y exportación a vídeo (captura con Playwright o Remotion).
- `examples/tcf.html`: motion de referencia (Tax Control Frameworks, en español).

## Instalar

```bash
mkdir -p ~/.claude/skills && cp -R skills/motion-fiscal ~/.claude/skills/
```

Después, en Claude Code: `/motion-fiscal DEMPE` o simplemente "hazme un motion sobre establecimiento permanente".
