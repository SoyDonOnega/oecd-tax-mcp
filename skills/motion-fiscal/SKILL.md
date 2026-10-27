---
name: motion-fiscal
description: Crea un motion explicativo (vídeo HTML animado 1920x1080) que ilustra un término fiscal, con el estilo de la serie GloBE/TCF y fuentes OCDE verificadas. Úsala cuando pidan un motion, vídeo, animación o visual de un concepto tributario.
---

# Motion fiscal

Convierte un término fiscal (GloBE, TCF, DEMPE, establecimiento permanente, CbCR…) en un motion de 45 a 75 segundos: una sola página HTML autocontenida, 1920x1080, donde cada fotograma es una función pura del tiempo `t`. Toda la serie comparte el mismo motor y el mismo aspecto, así que un motion nuevo se reconoce como parte de la colección.

Referencias de la serie: `GloBE in Five Steps` (inglés, Pilar Dos) y `examples/tcf.html` (español, Tax Control Frameworks). Si tienes acceso a `examples/tcf.html`, léelo antes de escribir: es el patrón canónico.

## Flujo: del término al motion

1. **Fija el término y el idioma.** Por defecto, español en pantalla. Nombre oficial en inglés como etiqueta secundaria (`.lab` o `.en`) cuando el término nace en un texto OCDE.
2. **Investiga con fuentes primarias.**
   - Si el MCP `oecd-tax` está conectado: `oecd_tax_search("<término>")` → `oecd_tax_resolve(id)` → `oecd_tax_get(id, query="<artículo o párrafo>")`. Para cifras, `oecd_stats_search` / `oecd_stats_query` (agencia `OECD.CTP.TPS`). Anota `cite_as` y el pinpoint (artículo, párrafo, página).
   - IDs útiles del catálogo: `oecd:pillar2-nutshell`, `oecd:pillar2-commentary-2022`, `oecd:pillar2-ag-2023-07`, `oecd:pillar2-handbook`, `oecd:tpg-2022`, `oecd:mtc-2017-condensed`, `oecd:coop-compliance-2013`, `oecd:tax-intermediaries-2008`, `oecd:tax-coop-progress-2024`.
   - Sin MCP: usa los PDF oficiales de la OCDE (o de la administración nacional: AEAT, BOE, UNE…) y dilo en la entrega. Nunca presentes como "recuperado vía MCP" algo que viene de memoria.
3. **Escribe el guion de escenas antes del HTML.** Una tabla con: escena, segundos `[inicio, fin]`, eyebrow, titular, qué se mueve, fuente. Forma típica (5 o 6 escenas):
   - **S0 Gancho (5 a 7 s):** una cifra o sigla gigante (380px) + definición en una frase.
   - **S1 Contexto:** el problema que resuelve o los actores (cajas + flechas).
   - **S2 Mecánica:** los pasos, bloques o fórmula. Un elemento cada 3 a 4,5 s, resaltado de uno en uno.
   - **S3 Consecuencia:** comparación antes/después, línea de tiempo o ejemplo numérico.
   - **S4 Aterrizaje:** cómo se aplica en España (o la jurisdicción pedida), con años y normas.
   - **Cierre:** una frase que resume la idea, con borde superior negro de 2px.
4. **Construye el HTML** copiando la plantilla de abajo, sin tocar el motor. Solo cambias `<title>`, las escenas, la constante `T` y el `max` del deslizador.
5. **Verifica:** abre con `?render`, llama a `seek(t)` en 5 o 6 instantes clave por escena y comprueba que no hay textos solapados ni fuera del lienzo (margen lateral 140px, nada por debajo de la `.rule` salvo `.src` y `.tag`). Comprueba que cada cifra y cada cita coinciden con la fuente.
6. **Entrega:** publícalo como Artifact (o guarda el `.html` donde pidan) y lista las fuentes usadas y qué partes son ilustrativas.

## Reglas de rigor

- **Cada escena con contenido normativo lleva `.src`** abajo a la izquierda, en mono: documento + pinpoint. Ej.: `Model Rules Art. 5.2.1 · Commentary on Art. 5.2.1, para. 15`, `OCDE FTA (2016), cap. 3`.
- **Lo ilustrativo se marca** con `.tag` abajo a la derecha: `Esquema, no datos`, `Datos de ejemplo · EUR m`, `Orden de las reglas`. Cualquier cifra inventada para un ejemplo lleva `Datos de ejemplo`. Los plazos esquemáticos se mencionan también en `.hint`.
- **Soft law no es norma vinculante.** Las directrices OCDE se presentan como guía o modelo; si hablas de obligación, cita la norma nacional o la directiva UE que la incorpora.
- **Sin cifras de memoria** si hay forma de comprobarlas. Umbrales, tipos y fechas se verifican en la fuente antes de animarlos. Si no se pudieron verificar, dilo en la entrega.
- **Fecha de recuperación** en la última escena cuando uses el MCP: `Recuperado el <fecha> vía oecd-tax MCP`.
- No reproduzcas párrafos largos de la OCDE: parafrasea y atribuye.

## Estilo visual (fijo para toda la serie)

- Fondo `#FAFAF8`, tinta `#0A0A0A`, gris `#666666`, líneas `#CCCCCC`, papel `#FFFFFF`. Un único tema claro; nada de color de acento.
- Tipos: Inter (400/500/600) para texto, JetBrains Mono para fuentes, años, etiquetas técnicas y cifras de apoyo. `font-feature-settings: "tnum"`.
- Rejilla: margen 140px a izquierda y derecha. Eyebrow en `top:96px`, titular en `top:190px`, `.rule` a 140px del fondo, `.src`/`.tag` a 84px del fondo.
- Jerarquía: gancho 380px, `.h1` 64px, `.big` 150px, `.desc h3` 60px, cuerpo 26 a 34px, etiquetas 18 a 20px en versalitas con tracking `.2em`.
- Formas: cajas con borde negro de 2px, sin sombras ni esquinas redondeadas. Resaltado = invertir (fondo tinta, texto papel). Flechas de 2px con punta CSS. Puntos sólidos o huecos en líneas de tiempo.
- Movimiento: el texto sube enmascarado (`.m[data-t]`), los elementos entran con opacidad + 24 a 30px de desplazamiento, las líneas crecen en anchura. Curvas `out` (exponencial) e `io` (cúbica). Las escenas cruzan con fundido de 0,4s y 18px.
- Frases cortas en pantalla. Una idea por titular. Sin rayas largas como puntuación.

## API del motor

- `<section class="scene" data-s="inicio,fin">`: ventana de la escena en segundos.
- `<div class="m" data-t="t0"><div>…</div></div>`: texto que sube enmascarado desde `t0`.
- `data-a='[["prop",t0,t1,v0,v1,"unidad"], …]'`: animación por propiedad. `prop` puede ser `opacity`, `x`, `y` (px, se combinan en `translate`) o cualquier propiedad CSS (`width` con `"px"`). Varias filas de la misma propiedad se encadenan: la posterior toma el control solo cuando empieza.
- `window.seek(t)` dibuja el instante `t`; `window.ready` pasa a `true` cuando cargan las fuentes. `?render` quita controles y fija el escenario a 1920x1080 sin escalar.
- Controles: espacio reproduce o pausa, flechas avanzan un fotograma (1/60 s), R reinicia. Respeta `prefers-reduced-motion`.
- Para listas largas (bloques, pasos) genera los elementos en JS antes de recoger `scenes/rises/anims`, como hace `tcf.html` con los seis bloques.

## Plantilla

```html
<title>NOMBRE DEL TÉRMINO</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Serie motion fiscal: un escenario 1920x1080, cada fotograma es función pura de t. Tema claro fijo. */
:root {
  --bg: #FAFAF8; --ink: #0A0A0A; --mute: #666666; --line: #CCCCCC; --paper: #FFFFFF;
  --sans: "Inter", "Helvetica Neue", Arial, sans-serif;
  --mono: "JetBrains Mono", "IBM Plex Mono", ui-monospace, Menlo, monospace;
  color-scheme: light;
}
html, body { background: var(--bg); color: var(--ink); }
body { font-family: var(--sans); padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px; }
.wrap { max-width: 1280px; margin: 0 auto; display: grid; gap: 14px; }
.frame { position: relative; width: 100%; aspect-ratio: 16 / 9; max-width: 100%; overflow: hidden; border: 1px solid var(--line); background: var(--bg); }
#stage { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; background: var(--bg); overflow: hidden; font-feature-settings: "tnum" 1; }
.bar { display: flex; align-items: center; gap: 14px; font: 500 12px/1 var(--mono); color: var(--mute); }
.bar button { font: 600 11px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--ink); background: var(--paper); border: 1px solid var(--ink); padding: 9px 14px; cursor: pointer; min-width: 84px; }
.bar button:focus-visible, .bar input:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
.bar input[type=range] { flex: 1; min-width: 0; accent-color: #0A0A0A; }
.hint { font: 400 12px/1.5 var(--mono); color: var(--mute); }
body.render { padding: 0; }
body.render .wrap { max-width: none; display: block; }
body.render .frame { border: 0; width: 1920px; height: 1080px; aspect-ratio: auto; }
body.render .bar, body.render .hint { display: none; }

.eyebrow { position: absolute; left: 140px; top: 96px; font: 600 20px/1 var(--sans); letter-spacing: .22em; text-transform: uppercase; }
.eyebrow span { color: var(--mute); }
.src { position: absolute; left: 140px; bottom: 84px; font: 400 19px/1.4 var(--mono); color: var(--mute); }
.tag { position: absolute; right: 140px; bottom: 84px; font: 500 17px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--mute); border: 1px solid var(--line); padding: 10px 14px; }
.rule { position: absolute; left: 140px; right: 140px; bottom: 140px; height: 1px; background: var(--line); }
#prog { position: absolute; left: 0; bottom: 0; height: 4px; background: var(--ink); width: 0; }
.scene { position: absolute; inset: 0; opacity: 0; }
.m { overflow: hidden; display: block; padding-bottom: .08em; }
.m > * { display: block; will-change: transform; }
.h1 { font: 600 64px/1.12 var(--sans); letter-spacing: -.02em; }
.h2 { font: 400 34px/1.35 var(--sans); color: var(--mute); }
.lab { font: 600 18px/1 var(--sans); letter-spacing: .2em; text-transform: uppercase; color: var(--mute); }
.big { font: 600 150px/1 var(--sans); letter-spacing: -.04em; }
.abs { position: absolute; }
.mono { font-family: var(--mono); }
.close { font: 600 34px/1.3 var(--sans); border-top: 2px solid var(--ink); padding-top: 20px; }
/* Estilos propios de las escenas de este término, debajo. */
</style>

<div class="wrap">
  <div class="frame" id="frame">
    <div id="stage">

      <!-- S0 gancho -->
      <section class="scene" data-s="0,6">
        <div class="eyebrow">ÁMBITO <span>· INSTRUMENTO OCDE</span></div>
        <div class="abs" style="left:126px; top:230px;">
          <div class="m" data-t="0.3"><div style="font:600 380px/0.9 var(--sans); letter-spacing:-.06em;">SIGLA</div></div>
        </div>
        <div class="abs" style="left:140px; top:620px; width:1400px;">
          <div class="m" data-t="1.2"><div class="lab">Nombre oficial en inglés · Traducción</div></div>
          <div class="m" data-t="1.7" style="margin-top:26px;"><div class="h1">Definición en una frase.</div></div>
        </div>
        <div class="rule"></div>
        <div class="src">Documento OCDE, artículo o párrafo</div>
      </section>

      <!-- S1 ejemplo de escena: titular + elemento que entra + cierre -->
      <section class="scene" data-s="6,14">
        <div class="eyebrow">Paso 1 <span>· Qué se mide</span></div>
        <div class="abs" style="left:140px; top:190px; width:1640px;">
          <div class="m" data-t="6.4"><div class="h1">Titular de una sola idea.</div></div>
        </div>
        <div class="abs" style="left:140px; top:420px; width:640px; height:120px; border:2px solid var(--ink); background:var(--paper); display:grid; place-content:center;"
             data-a='[["opacity",7.2,7.7,0,1],["y",7.2,7.9,30,0]]'>
          <b style="font:600 40px/1 var(--sans);">Elemento</b>
        </div>
        <div class="abs" style="left:140px; top:780px; width:1640px;">
          <div class="m" data-t="10"><div class="close">Frase de cierre de la escena.</div></div>
        </div>
        <div class="rule"></div>
        <div class="src">Fuente con pinpoint</div>
        <div class="tag">Datos de ejemplo</div>
      </section>

      <div id="prog"></div>
    </div>
  </div>
  <div class="bar">
    <button id="play" type="button">Pausa</button>
    <input id="scrub" type="range" min="0" max="14" step="0.01" value="0" aria-label="Línea de tiempo">
    <span id="clock">0.0 / 14.0 s</span>
  </div>
  <div class="hint">Espacio: reproducir o pausar · ← → avanzar un fotograma · R: volver a empezar.</div>
</div>

<script>
(() => {
  // Duración total: igual al fin de la última escena y al max del deslizador.
  const T = 14;
  // Aquí, si hace falta, generar elementos repetidos (bloques, pasos) antes de recogerlos abajo.

  const render = /[?&]render/.test(location.search);
  if (render) document.body.classList.add('render');
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const out = x => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(2, -10 * x) * (1 - x * 0.001);
  const io = x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;

  const scenes = [...document.querySelectorAll('.scene')].map(el => ({ el, s: el.dataset.s.split(',').map(Number) }));
  const rises = [...document.querySelectorAll('.m[data-t]')].map(el => ({ inner: el.firstElementChild, t: +el.dataset.t }));
  const anims = [...document.querySelectorAll('[data-a]')].map(el => ({ el, k: JSON.parse(el.dataset.a) }));
  const prog = document.getElementById('prog');

  window.seek = t => {
    for (const { el, s } of scenes) {
      const a = s[0] === 0 ? 1 : out(seg(t, s[0], s[0] + .4)), b = io(seg(t, s[1] - .45, s[1]));
      const o = s[1] >= T ? a : a * (1 - b);
      el.style.opacity = o;
      el.style.transform = `translateY(${(1 - a) * 18 - (s[1] >= T ? 0 : b * 18)}px)`;
      el.style.visibility = o > 0 ? 'inherit' : 'hidden';
    }
    for (const { inner, t: t0 } of rises) {
      const p = out(seg(t, t0, t0 + .7));
      inner.style.transform = `translateY(${(1 - p) * 108}%)`;
    }
    for (const { el, k } of anims) {
      let x = 0, y = 0;
      const seen = new Set();
      for (const [prop, t0, t1, v0, v1, unit = ''] of k) {
        // las filas posteriores de una misma propiedad solo mandan desde que empiezan
        if (seen.has(prop) && t < t0) continue;
        seen.add(prop);
        const v = v0 + (v1 - v0) * io(seg(t, t0, t1));
        if (prop === 'x') x = v; else if (prop === 'y') y = v;
        else el.style[prop] = v + unit;
      }
      if (k.some(r => r[0] === 'x' || r[0] === 'y')) el.style.transform = `translate(${x}px, ${y}px)`;
    }
    prog.style.width = (t / T * 100) + '%';
  };

  const frame = document.getElementById('frame'), stage = document.getElementById('stage');
  const fit = () => { if (!render) stage.style.transform = `scale(${frame.clientWidth / 1920})`; };
  addEventListener('resize', fit); fit();

  let t = 0, playing = !render && !matchMedia('(prefers-reduced-motion: reduce)').matches, last = null;
  const btn = document.getElementById('play'), scrub = document.getElementById('scrub'), clock = document.getElementById('clock');
  const show = () => { seek(t); scrub.value = t; clock.textContent = `${t.toFixed(1)} / ${T.toFixed(1)} s`; btn.textContent = playing ? 'Pausa' : 'Reproducir'; };
  const tick = now => {
    if (playing) { if (last !== null) t += (now - last) / 1000; if (t >= T) { t = T; playing = false; } show(); }
    last = now; requestAnimationFrame(tick);
  };
  const toggle = () => { if (t >= T) t = 0; playing = !playing; show(); };
  btn.addEventListener('click', toggle);
  scrub.addEventListener('input', () => { t = +scrub.value; playing = false; show(); });
  addEventListener('keydown', e => {
    if (render) return;
    if (e.code === 'Space') { e.preventDefault(); toggle(); }
    else if (e.key === 'ArrowRight') { playing = false; t = Math.min(T, t + 1 / 60); show(); }
    else if (e.key === 'ArrowLeft') { playing = false; t = Math.max(0, t - 1 / 60); show(); }
    else if (e.key === 'r' || e.key === 'R') { t = 0; playing = true; show(); }
  });
  // Con movimiento reducido, mostrar un fotograma representativo del gancho.
  if (!playing && !render) t = 4.5;
  show();
  document.fonts.ready.then(() => { window.ready = true; if (!render) requestAnimationFrame(tick); });
})();
</script>
```

## Exportar a vídeo (opcional)

**Opción A, captura directa (recomendada).** El motor ya es determinista, así que basta con fotografiar cada fotograma:

```js
// capture.mjs: node capture.mjs motion.html 64  →  frames/00000.png …
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const [file, T, fps = 30] = process.argv.slice(2);
mkdirSync('frames', { recursive: true });
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(pathToFileURL(file).href + '?render');
await p.waitForFunction(() => window.ready === true);
for (let i = 0, n = Math.round(T * fps); i <= n; i++) {
  await p.evaluate(t => window.seek(t), i / fps);
  await p.screenshot({ path: `frames/${String(i).padStart(5, '0')}.png` });
}
await b.close();
```

Luego `ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 motion.mp4`.

**Opción B, Remotion** (cuando quieran editar en React, añadir voz o montar varios motions):

- `npx create-video@latest`, composición de 1920x1080 a 30 fps con `durationInFrames = T * 30`.
- Cada escena es un `<Sequence from={inicio*fps} durationInFrames={(fin-inicio)*fps}>`; dentro, `const t = useCurrentFrame() / fps + inicio`.
- Reutiliza `seg`, `out` e `io` tal cual (o `interpolate` con `Easing.bezier`), y traduce cada `data-a` a estilos calculados desde `t`. No uses animaciones CSS ni `transition`: Remotion solo ve el fotograma actual.
- Fuentes con `@remotion/google-fonts/Inter` y `@remotion/google-fonts/JetBrainsMono`; espera a `loadFont()` antes de renderizar.
- `npx remotion render <Composición> out/motion.mp4`.
- Mantén las mismas `.src` y `.tag` en pantalla: el rigor no cambia por cambiar de formato.
