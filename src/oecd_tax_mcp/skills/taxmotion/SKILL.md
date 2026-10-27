---
name: taxmotion
description: Creates an explainer motion (animated 1920x1080 HTML video) that illustrates a tax term, in the style of the GloBE/TCF series and with verified OECD sources. The motion is written in the language the user writes in. Use when the user runs /taxmotion <term> or asks for a motion, video, animation or visual of a tax concept.
license: MIT
argument-hint: "<tax term>"
disable-model-invocation: true
---

# Taxmotion

Turns a tax term (GloBE, TCF, DEMPE, permanent establishment, CbCR…) into a motion of 45 to 75 seconds: one self-contained HTML page, 1920x1080, where each frame is a pure function of time `t`. The whole series shares the same engine and the same look, so a new motion reads as part of the collection.
Paths in this file are relative to the skill root (the folder that contains this SKILL.md).

Series references: `GloBE in Five Steps` (English, Pillar Two) and `assets/tcf.html` (Spanish, Tax Control Frameworks). If you can read `assets/tcf.html`, read it before you write: it is the canonical pattern. Copy its structure and engine, not its language.

## Output language

- **Write every word on screen in the language the user writes in.** If the user explicitly asks for another language, use that one. Ignore the language of the sources and of these instructions.
- This covers headlines, labels, `.src` connectors, `.tag` texts, the closing line and the player UI (play/pause button, timeline `aria-label`, clock, keyboard hint).
- When the output language is not English and the term comes from an OECD text, show the official English name as a secondary label (`.lab` or `.en`).
- Keep official document titles, article numbers and acronyms as published (`Model Rules Art. 5.2.1`, `CbCR`).
- Number and date formats follow the output language (`EUR 750 m` / `750 M EUR`, `1.5` / `1,5`).

## Workflow: from term to motion

1. **Fix the term and the output language** (see above).
2. **Research with primary sources.**
   - If the `oecd-tax` MCP is connected: `oecd_tax_search("<term>")` → `oecd_tax_resolve(id)` → `oecd_tax_get(id, query="<article or paragraph>")`. For figures, `oecd_stats_search` / `oecd_stats_query` (agency `OECD.CTP.TPS`). Write down `cite_as` and the pinpoint (article, paragraph, page).
   - Useful catalogue ids: `oecd:pillar2-nutshell`, `oecd:pillar2-commentary-2022`, `oecd:pillar2-ag-2023-07`, `oecd:pillar2-handbook`, `oecd:tpg-2022`, `oecd:mtc-2017-condensed`, `oecd:coop-compliance-2013`, `oecd:tax-intermediaries-2008`, `oecd:tax-coop-progress-2024`.
   - Without the MCP: use the official OECD PDFs (or the national administration's: AEAT, BOE, UNE…) and say so in the delivery. Never present something from memory as "retrieved via MCP".
3. **Write the scene script before the HTML.** A table with: scene, seconds `[start, end]`, eyebrow, headline, what moves, source. Typical shape (5 or 6 scenes):
   - **S0 Hook (5 to 7 s):** one giant figure or acronym (380px) + a one-sentence definition.
   - **S1 Context:** the problem it solves or the actors (boxes + arrows).
   - **S2 Mechanics:** the steps, blocks or formula. One element every 3 to 4.5 s, highlighted one at a time.
   - **S3 Consequence:** before/after comparison, timeline or numeric example.
   - **S4 Landing:** how it applies in Spain (or the jurisdiction the user asks for), with years and rules.
   - **Close:** one sentence that sums up the idea, with a 2px black top border.
4. **Build the HTML** by copying the template below without touching the engine. Change only `<title>`, the scenes, the constant `T`, the slider `max` and the UI strings (into the output language).
5. **Verify:** open with `?render`, call `seek(t)` at 5 or 6 key moments per scene and check that no text overlaps or leaves the canvas (140px side margin, nothing below the `.rule` except `.src` and `.tag`). Check that every figure and every citation matches the source.
6. **Deliver:** publish it as an Artifact (or save the `.html` where asked) and list the sources used and which parts are illustrative.

## Accuracy rules

- **Every scene with normative content carries `.src`** at the bottom left, in mono: document + pinpoint. E.g. `Model Rules Art. 5.2.1 · Commentary on Art. 5.2.1, para. 15`, `OECD FTA (2016), ch. 3`.
- **Mark what is illustrative** with `.tag` at the bottom right: `Diagram, not data`, `Example data · EUR m`, `Order of the rules` (translated into the output language). Any figure invented for an example carries `Example data`. Schematic timelines are also mentioned in `.hint`.
- **Soft law is not binding law.** OECD guidelines are presented as guidance or a model; if you talk about an obligation, cite the national rule or the EU directive that implements it.
- **No figures from memory** when they can be checked. Thresholds, rates and dates are verified in the source before you animate them. If they could not be verified, say so in the delivery.
- **Retrieval date** in the last scene when you use the MCP: `Retrieved on <date> via oecd-tax MCP` (in the output language).
- Do not reproduce long OECD paragraphs: paraphrase and attribute.

## Visual style (fixed for the whole series)

- Background `#FAFAF8`, ink `#0A0A0A`, gray `#666666`, lines `#CCCCCC`, paper `#FFFFFF`. One light theme only; no accent color.
- Type: Inter (400/500/600) for text, JetBrains Mono for sources, years, technical labels and supporting figures. `font-feature-settings: "tnum"`.
- Grid: 140px margin left and right. Eyebrow at `top:96px`, headline at `top:190px`, `.rule` 140px from the bottom, `.src`/`.tag` 84px from the bottom.
- Hierarchy: hook 380px, `.h1` 64px, `.big` 150px, `.desc h3` 60px, body 26 to 34px, labels 18 to 20px in small caps with `.2em` tracking.
- Shapes: boxes with a 2px black border, no shadows or rounded corners. Highlight = invert (ink background, paper text). 2px arrows with a CSS head. Solid or hollow dots on timelines.
- Motion: text rises masked (`.m[data-t]`), elements enter with opacity + 24 to 30px offset, lines grow in width. Curves `out` (exponential) and `io` (cubic). Scenes cross-fade over 0.4s and 18px.
- Short sentences on screen. One idea per headline. No em dashes as punctuation.

## Engine API

- `<section class="scene" data-s="start,end">`: the scene window in seconds.
- `<div class="m" data-t="t0"><div>…</div></div>`: text that rises masked from `t0`.
- `data-a='[["prop",t0,t1,v0,v1,"unit"], …]'`: per-property animation. `prop` can be `opacity`, `x`, `y` (px, combined into `translate`) or any CSS property (`width` with `"px"`). Several rows for the same property chain: a later row takes over only once it starts.
- `window.seek(t)` draws instant `t`; `window.ready` turns `true` once the fonts load. `?render` removes the controls and fixes the stage at 1920x1080 without scaling.
- Controls: space plays or pauses, arrows step one frame (1/60 s), R restarts. Respects `prefers-reduced-motion`.
- For long lists (blocks, steps) generate the elements in JS before collecting `scenes/rises/anims`, as `tcf.html` does with its six blocks.

## Template

Placeholder text and UI strings are in English: replace them with the output language.

```html
<title>TERM NAME</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* taxmotion series: one 1920x1080 stage, each frame is a pure function of t. Fixed light theme. */
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
/* Styles specific to this term's scenes, below. */
</style>

<div class="wrap">
  <div class="frame" id="frame">
    <div id="stage">

      <!-- S0 hook -->
      <section class="scene" data-s="0,6">
        <div class="eyebrow">SCOPE <span>· OECD INSTRUMENT</span></div>
        <div class="abs" style="left:126px; top:230px;">
          <div class="m" data-t="0.3"><div style="font:600 380px/0.9 var(--sans); letter-spacing:-.06em;">ACRONYM</div></div>
        </div>
        <div class="abs" style="left:140px; top:620px; width:1400px;">
          <div class="m" data-t="1.2"><div class="lab">Official English name · Translation</div></div>
          <div class="m" data-t="1.7" style="margin-top:26px;"><div class="h1">One-sentence definition.</div></div>
        </div>
        <div class="rule"></div>
        <div class="src">OECD document, article or paragraph</div>
      </section>

      <!-- S1 sample scene: headline + entering element + close -->
      <section class="scene" data-s="6,14">
        <div class="eyebrow">Step 1 <span>· What is measured</span></div>
        <div class="abs" style="left:140px; top:190px; width:1640px;">
          <div class="m" data-t="6.4"><div class="h1">A headline with one idea.</div></div>
        </div>
        <div class="abs" style="left:140px; top:420px; width:640px; height:120px; border:2px solid var(--ink); background:var(--paper); display:grid; place-content:center;"
             data-a='[["opacity",7.2,7.7,0,1],["y",7.2,7.9,30,0]]'>
          <b style="font:600 40px/1 var(--sans);">Element</b>
        </div>
        <div class="abs" style="left:140px; top:780px; width:1640px;">
          <div class="m" data-t="10"><div class="close">Closing sentence of the scene.</div></div>
        </div>
        <div class="rule"></div>
        <div class="src">Source with pinpoint</div>
        <div class="tag">Example data</div>
      </section>

      <div id="prog"></div>
    </div>
  </div>
  <div class="bar">
    <button id="play" type="button">Pause</button>
    <input id="scrub" type="range" min="0" max="14" step="0.01" value="0" aria-label="Timeline">
    <span id="clock">0.0 / 14.0 s</span>
  </div>
  <div class="hint">Space: play or pause · ← → step one frame · R: restart.</div>
</div>

<script>
(() => {
  // Total duration: equal to the end of the last scene and to the slider max.
  const T = 14;
  // Player button labels, in the output language.
  const L = { play: 'Play', pause: 'Pause' };
  // If needed, generate repeated elements (blocks, steps) here, before they are collected below.

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
        // later rows for the same property take over only once they start
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
  const show = () => { seek(t); scrub.value = t; clock.textContent = `${t.toFixed(1)} / ${T.toFixed(1)} s`; btn.textContent = playing ? L.pause : L.play; };
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
  // With reduced motion, show a representative frame of the hook.
  if (!playing && !render) t = 4.5;
  show();
  document.fonts.ready.then(() => { window.ready = true; if (!render) requestAnimationFrame(tick); });
})();
</script>
```

## Export to video (optional)

**Option A, direct capture (recommended).** The engine is already deterministic, so it is enough to screenshot each frame:

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

Then `ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 motion.mp4`.

**Option B, Remotion** (when they want to edit in React, add voice-over or assemble several motions):

- `npx create-video@latest`, a 1920x1080 composition at 30 fps with `durationInFrames = T * 30`.
- Each scene is a `<Sequence from={start*fps} durationInFrames={(end-start)*fps}>`; inside it, `const t = useCurrentFrame() / fps + start`.
- Reuse `seg`, `out` and `io` as they are (or `interpolate` with `Easing.bezier`), and translate each `data-a` into styles computed from `t`. Do not use CSS animations or `transition`: Remotion only sees the current frame.
- Fonts with `@remotion/google-fonts/Inter` and `@remotion/google-fonts/JetBrainsMono`; wait for `loadFont()` before rendering.
- `npx remotion render <Composition> out/motion.mp4`.
- Keep the same `.src` and `.tag` on screen: the accuracy rules do not change with the format.
