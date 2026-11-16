// Verifica stills de cada cena: fonte carregada, escala mínima, cobertura e paleta.
// Uso: node scripts/check-render.mjs [--fonts] [--scale] [--safe-zone] [--transitions] [--words] [--media]
//        [--fill] [--cta] [--split] [--style <id>] [--all]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { readFileSync, mkdtempSync, rmSync, mkdirSync, readdirSync, symlinkSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { inflateSync } from "node:zlib";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repo = path.resolve(root, "..");
const args = process.argv.slice(2);
const flag = (n) => args.includes(`--${n}`);
const styleId = args.includes("--style") ? args[args.indexOf("--style") + 1] : null;
const FLAGS = ["fonts", "scale", "safe-zone", "transitions", "words", "media", "fill", "cta", "split"];
const picked = FLAGS.some(flag);
const all = flag("all") || (!picked && !styleId);
/** `--style X` roda as checagens de cena do estilo; as flags isoladas restringem. */
const want = (n) => all || flag(n) || (!!styleId && !picked);
const sceneChecks = all || ["fonts", "scale", "safe-zone", "fill"].some(flag) || (!!styleId && !picked);
const SAFE_STYLES = ["isometric-pastel", "forge-motion"];
const readJson = (p) => JSON.parse(readFileSync(p, "utf8"));

// Mesmos limites de render/src/safeZone.ts (DUP-03: o script lê o arquivo, sem cópia).
const SAFE = Object.fromEntries([...readFileSync(path.join(root, "src/safeZone.ts"), "utf8")
  .matchAll(/^\s+(top|bottom|rightGuard|lowerHalf): (\d+),/gm)].map((m) => [m[1], Number(m[2])]));
const WIDTH = 1080;

const theme = readJson(path.join(repo, "themes/forge.json"));
const SCENES_ALL = [
  { type: "title", dur: 3, narration: "", text: "Automatize esse processo de ponta a ponta" },
  { type: "highlight", dur: 3, narration: "", text: "Tudo roda local, sem enviar nada" },
  { type: "flow", dur: 5, narration: "", steps: ["Extrair áudio", "Transcrever local", "Escolher trechos", "Gerar reel"] },
  { type: "list", dur: 4, narration: "", items: ["Sem nuvem", "Sem custo por minuto", "Controle total"] },
  { type: "compare", dur: 4, narration: "",
    left: { label: "Antes", points: ["Edição manual", "Horas por vídeo"] },
    right: { label: "Depois", points: ["Pipeline local", "Minutos por vídeo"] } },
  { type: "cta", dur: 3, narration: "", text: "Quer ver mais?" },
];
const scenesFor = (style) => SCENES_ALL.filter((s) => style.scene_types.includes(s.type));
/** Props como o motor entrega ao render (paleta e contraste resolvidos em core/render.py, DUP-01). */
const engineProps = (scenes, themeId, styleId) => {
  const code = "import json,sys;from reel_studio.core import contracts,render;"
    + "t=contracts.load_theme(sys.argv[2]);s=contracts.load_style(sys.argv[3]);"
    + "print(json.dumps(render.props({'scenes':json.loads(sys.argv[1])},t,s)))";
  const r = spawnSync("uv", ["run", "python", "-c", code, JSON.stringify(scenes), themeId, styleId],
    { cwd: path.join(repo, "engine"), encoding: "utf8" });
  if (r.status !== 0) throw new Error(r.stderr);
  return JSON.parse(r.stdout);
};
/** Props da camada `Overlay` como o motor entrega (core/overlay.py). */
const overlayProps = (overlays, length) => {
  const code = "import json,sys;from pathlib import Path;from reel_studio.core import contracts,overlay;"
    + "from reel_studio.core.cut import CutJob;o=json.loads(sys.argv[1]);"
    + "j=CutJob('clip-01','c.ass','',Path('o.mp4'),[],end=float(sys.argv[2]),overlays=tuple(o));"
    + "print(json.dumps(overlay.layer_props(j,contracts.load_theme('forge'))))";
  const r = spawnSync("uv", ["run", "python", "-c", code, JSON.stringify(overlays), String(length)],
    { cwd: path.join(repo, "engine"), encoding: "utf8" });
  if (r.status !== 0) throw new Error(r.stderr);
  return JSON.parse(r.stdout);
};
// Todos os tipos de componente visíveis ao mesmo tempo: pior caso de sobreposição das faixas.
const OVERLAY_SAMPLE = [
  { at: 0, dur: 6, type: "hook", text: "Pare de editar vídeo na mão" },
  { at: 0, dur: 6, type: "keyword", text: "`forge-sdd`" },
  { at: 0, dur: 6, type: "step", text: "Gravar a tela" },
  { at: 0, dur: 6, type: "step", text: "Gerar o reel" },
  { at: 0, dur: 6, type: "callout", text: "Tudo roda local" },
  { at: 0, dur: 6, type: "keyword", text: "`no-topo`", pos: "top" },
  { at: 0, dur: 6, type: "step", text: "Passo no topo", pos: "top" },
  { at: 0, dur: 6, type: "progress" },
  { at: 0, dur: 6, type: "cta", text: "npx @nathanramorim/forge-sdd init" },
  { at: 0, dur: 6, type: "logo" },
];
/** Faixa da legenda lida das mesmas constantes do motor (DUP-03), não de números soltos aqui. */
const captionBand = () => {
  const margin = Number(/"lower-third": (\d+)/.exec(readFileSync(path.join(repo, "engine/src/reel_studio/core/captions.py"), "utf8"))[1]);
  const bottom = 1920 - margin, top = bottom - 2 * theme.caption.size * 1.25;
  const region = Object.fromEntries([...readFileSync(path.join(root, "src/overlay/regions.ts"), "utf8")
    .matchAll(/CAPTION = \{ top: (\d+), bottom: (\d+) \}/g)].flatMap((m) => [["top", Number(m[1])], ["bottom", Number(m[2])]]));
  return { top: Math.min(top, region.top), bottom: Math.max(bottom, region.bottom), declared: region };
};
const STYLES = ["isometric-pastel", "flat-vector-science", "whiteboard-explainer"];

const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

/** Decodifica PNG 8 bits RGB/RGBA sem entrelaçamento. */
const decodePng = (buf) => {
  let pos = 8, w = 0, h = 0, ch = 4;
  const idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos), type = buf.toString("ascii", pos + 4, pos + 8);
    const data = buf.subarray(pos + 8, pos + 8 + len);
    if (type === "IHDR") { w = data.readUInt32BE(0); h = data.readUInt32BE(4); ch = data[9] === 6 ? 4 : 3; }
    if (type === "IDAT") idat.push(data);
    pos += 12 + len;
  }
  const raw = inflateSync(Buffer.concat(idat)), stride = w * ch, px = Buffer.alloc(h * stride);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], line = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    for (let x = 0; x < stride; x++) {
      const a = x >= ch ? px[y * stride + x - ch] : 0, b = y ? px[(y - 1) * stride + x] : 0;
      const c = x >= ch && y ? px[(y - 1) * stride + x - ch] : 0;
      const pa = Math.abs(b - c), pb = Math.abs(a - c), pc = Math.abs(a + b - 2 * c);
      const pred = [0, a, b, (a + b) >> 1, pa <= pb && pa <= pc ? a : pb <= pc ? b : c][f];
      px[y * stride + x] = (line[x] + pred) & 255;
    }
  }
  return { w, h, ch, px };
};

/** Cobertura vertical, maior faixa vazia, fundo e cores da paleta presentes. */
const analyze = ({ w, h, ch, px }, bg, palette) => {
  const at = (x, y) => [0, 1, 2].map((k) => px[(y * w + x) * ch + k]);
  const near = (a, b, t) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) <= t;
  const rows = [];
  const found = new Set();
  for (let y = 0; y < h; y++) {
    let busy = false;
    for (let x = 0; x < w; x += 3) {
      const c = at(x, y);
      if (!near(c, bg, 24)) busy = true;
      palette.forEach((p, i) => { if (near(c, p, 6)) found.add(i); });
    }
    rows.push(busy);
  }
  const first = rows.indexOf(true), last = rows.lastIndexOf(true);
  let gap = Math.max(first, h - 1 - last), run = 0;
  for (let y = first; y <= last; y++) { run = rows[y] ? 0 : run + 1; gap = Math.max(gap, run); }
  return { coverage: (last - first) / (h - 160), gap: gap / h, corner: at(2, 2), colors: found.size };
};

const failures = [];
const check = (ok, msg) => { if (!ok) failures.push(msg); console.log(`${ok ? "ok  " : "FAIL"} ${msg}`); };

const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts"), publicDir: path.join(root, "public") });
const tmp = mkdtempSync(path.join(tmpdir(), "check-render-"));
try {
  for (const sid of !sceneChecks ? [] : all ? ["__default__", STYLES[0], "forge-motion"] : styleId ? [styleId] : flag("safe-zone") ? SAFE_STYLES : ["__default__"]) {
    const style = sid === "__default__" ? readJson(path.join(repo, "styles", STYLES[2], "style.json")) : readJson(path.join(repo, "styles", sid, "style.json"));
    const SCENES = scenesFor(style);
    for (let i = 0; i < SCENES.length; i++) {
      const scene = SCENES[i];
      const logs = [];
      const inputProps = { ...engineProps([scene], theme.id, style.id), probe: true };
      const composition = await selectComposition({ serveUrl, id: "Reel", inputProps });
      const out = path.join(tmp, `${style.id}-${scene.type}.png`);
      await renderStill({
        composition, serveUrl, output: out, inputProps, frame: Math.round(scene.dur * 30) - 5, imageFormat: "png",
        onBrowserLog: (l) => logs.push(l.text),
      });
      const tag = `${style.id}/${scene.type}`;
      const probe = JSON.parse((logs.find((t) => t.startsWith("[probe]")) ?? "[probe] {}").slice(8));
      if (want("fonts")) {
        check(!logs.some((t) => t.includes("[font-fallback]")), `${tag}: sem fallback de fonte`);
        check((probe.fonts ?? []).length > 0 && probe.fonts.every((f) => f.loaded && f.width !== f.serifWidth),
          `${tag}: texto em ${(probe.fonts ?? []).map((f) => f.family).join("+")} (largura difere da serifa)`);
      }
      if (want("scale")) {
        check(probe.minSize >= 44, `${tag}: menor texto ${probe.minSize}px >= 44px`);
      }
      if (want("safe-zone") && SAFE_STYLES.includes(style.id)) {
        const bad = (probe.boxes ?? []).filter((b) => b.top < SAFE.top - 0.5 || b.bottom > SAFE.bottom + 0.5
          || (b.bottom > SAFE.lowerHalf && b.right > WIDTH - SAFE.rightGuard + 0.5));
        check((probe.boxes ?? []).length > 0 && bad.length === 0,
          `${tag}: texto na zona segura (y ${SAFE.top}-${SAFE.bottom}, guarda ${SAFE.rightGuard}px)`
          + (bad.length ? ` fora: ${JSON.stringify(bad[0])}` : ""));
      }
      if (want("fill") && style.id === "forge-motion") {
        const cap = captionBand();
        // Cobertura vertical do conteúdo (painéis e texto) na zona útil e folga até a legenda.
        const spans = [...(probe.panels ?? []), ...(probe.boxes ?? [])]
          .map((b) => [Math.max(b.top, SAFE.top), Math.min(b.bottom, cap.top - 40)]).filter(([a, b]) => b > a)
          .sort((x, y) => x[0] - y[0]);
        const merged = [];
        for (const sp of spans) merged.length && sp[0] <= merged.at(-1)[1] ? merged.at(-1)[1] = Math.max(merged.at(-1)[1], sp[1]) : merged.push([...sp]);
        const useful = cap.top - 40 - SAFE.top;
        const gaps = merged.map((m, k) => m[0] - (k ? merged[k - 1][1] : SAFE.top)).concat(merged.length ? cap.top - 40 - merged.at(-1)[1] : useful);
        const empty = Math.max(...gaps) / useful;
        check(empty <= 0.15, `${tag}: faixa vazia vertical ${(empty * 100).toFixed(0)}% <= 15% da zona útil`);
        const bottoms = [...(probe.panels ?? []), ...(probe.boxes ?? [])].map((b) => b.bottom);
        const free = bottoms.length ? cap.top - Math.max(...bottoms) : 0;
        check(free >= 40, `${tag}: folga ${free.toFixed(0)}px >= 40px entre o conteúdo e a legenda (y ${cap.top.toFixed(0)})`);
      }
      if (all || styleId) {
        const palette = [...inputProps.style.look.palette.map(hex), hex(theme.colors.accent)];
        const a = analyze(decodePng(readFileSync(out)), hex(theme.colors.bg), palette);
        if (style.id === "forge-motion") {
          check(a.corner.every((v, k) => Math.abs(v - hex(theme.colors.bg)[k]) <= 8), `${tag}: fundo do tema ${theme.id}`);
          check(a.colors >= 2, `${tag}: ${a.colors} cores dos tokens do tema (>= 2)`);
        }
        if (style.id === "isometric-pastel") {
          if (scene.type === "flow") check(a.coverage >= 0.7, `${tag}: cobertura vertical ${(a.coverage * 100).toFixed(0)}% >= 70%`);
          check(a.gap <= 0.25, `${tag}: maior faixa vazia ${(a.gap * 100).toFixed(0)}% <= 25%`);
          check(a.corner.every((v, k) => Math.abs(v - hex(theme.colors.bg)[k]) <= 8), `${tag}: fundo do tema ${theme.id}`);
          check(a.colors >= 3, `${tag}: ${a.colors} cores da paleta (>= 3)`);
        }
      }
    }
  }
  if (sceneChecks && want("safe-zone")) {
    const props = { ...overlayProps(OVERLAY_SAMPLE, 6), probe: true };
    const composition = await selectComposition({ serveUrl, id: "Overlay", inputProps: props });
    const logs = [];
    await renderStill({ composition, serveUrl, output: path.join(tmp, "overlay.png"), inputProps: props,
      frame: 90, imageFormat: "png", onBrowserLog: (l) => logs.push(l.text) });
    const probe = JSON.parse((logs.find((t) => t.startsWith("[probe]")) ?? "[probe] {}").slice(8));
    const boxes = probe.boxes ?? [];
    const bad = boxes.filter((b) => b.top < SAFE.top - 0.5 || b.bottom > SAFE.bottom + 0.5
      || (b.bottom > SAFE.lowerHalf && b.right > WIDTH - SAFE.rightGuard + 0.5));
    check(boxes.length > 0 && bad.length === 0, `overlay: texto na zona segura (y ${SAFE.top}-${SAFE.bottom}, guarda ${SAFE.rightGuard}px)`
      + (bad.length ? ` fora: ${JSON.stringify(bad[0])}` : ""));
    const cap = captionBand();
    const mid = boxes.filter((b) => b.bottom > SAFE.lowerHalf);
    const hit = mid.filter((b) => b.top < cap.bottom && b.bottom > cap.top);
    check(hit.length === 0, `overlay: nenhum texto cobre a legenda (y ${cap.top.toFixed(0)}-${cap.bottom})`
      + (hit.length ? ` cobre: ${JSON.stringify(hit[0])}` : ""));
    const hits = (x, y) => x.left < y.right - 2 && y.left < x.right - 2 && x.top < y.bottom - 2 && y.top < x.bottom - 2;
    const overlap = boxes.some((x, i) => boxes.slice(i + 1).some((y) => hits(x, y)));
    check(!overlap, "overlay: faixas empilhadas sem sobreposição de texto");
    check(probe.minSize >= 44, `overlay: menor texto ${probe.minSize}px >= 44px`);
    check((probe.fonts ?? []).every((f) => f.loaded), "overlay: fontes carregadas");
  }
  const forge = readJson(path.join(repo, "styles/forge-motion/style.json"));
  /** Props do render com a cena trocada, e o probe de um quadro da linha do tempo. */
  const probeAt = async (inputProps, frame, url = serveUrl) => {
    const composition = await selectComposition({ serveUrl: url, id: "Reel", inputProps });
    const logs = [];
    const output = path.join(tmp, `f${frame}-${Math.random().toString(36).slice(2)}.png`);
    await renderStill({ composition, serveUrl: url, output, inputProps, frame, imageFormat: "png",
      onBrowserLog: (l) => logs.push(l.text) });
    return { probe: JSON.parse((logs.find((t) => t.startsWith("[probe]")) ?? "[probe] {}").slice(8)), output };
  };
  if (want("split")) {
    // 05-14: no `split` o vídeo fica em cima (y 250 a 950) e todo o texto abaixo dele, sem cobrir a legenda.
    const code = "import json;from reel_studio.core.cut import Layout,video_rect;"
      + "print(json.dumps(video_rect(Layout('split'),(2860,1776))))";
    const r = spawnSync("uv", ["run", "python", "-c", code], { cwd: path.join(repo, "engine"), encoding: "utf8" });
    if (r.status !== 0) throw new Error(r.stderr);
    const rect = JSON.parse(r.stdout);
    const splitRegion = Object.fromEntries([...readFileSync(path.join(root, "src/overlay/regions.ts"), "utf8")
      .matchAll(/video: \{ top: (\d+), bottom: (\d+) \}/g)].flatMap((m) => [["top", Number(m[1])], ["bottom", Number(m[2])]]));
    const sample = OVERLAY_SAMPLE.filter((o) => !o.pos);
    const props = { ...overlayProps(sample, 6), probe: true, layout: "split", presenter: true, frame: rect,
      speech: [[0, 6]] };
    const composition = await selectComposition({ serveUrl, id: "Overlay", inputProps: props });
    const logs = [];
    await renderStill({ composition, serveUrl, output: path.join(tmp, "split.png"), inputProps: props, frame: 90,
      imageFormat: "png", onBrowserLog: (l) => logs.push(l.text) });
    const probe = JSON.parse((logs.find((t) => t.startsWith("[probe]")) ?? "[probe] {}").slice(8));
    const boxes = probe.boxes ?? [];
    check(rect.top >= splitRegion.top && rect.top + rect.height <= splitRegion.bottom,
      `split: vídeo na faixa de cima (y ${rect.top}-${rect.top + rect.height}, faixa ${splitRegion.top}-${splitRegion.bottom})`);
    const onVideo = boxes.filter((b) => b.top < splitRegion.bottom);
    check(boxes.length > 0 && onVideo.length === 0, "split: nenhum texto sobre o vídeo (todo abaixo de y " + splitRegion.bottom + ")"
      + (onVideo.length ? ` cobre: ${JSON.stringify(onVideo[0])}` : ""));
    const bad = boxes.filter((b) => b.bottom > SAFE.bottom + 0.5 || (b.bottom > SAFE.lowerHalf && b.right > WIDTH - SAFE.rightGuard + 0.5));
    check(bad.length === 0, "split: texto na zona segura" + (bad.length ? ` fora: ${JSON.stringify(bad[0])}` : ""));
    const cap = captionBand();
    const hit = boxes.filter((b) => b.top < cap.bottom && b.bottom > cap.top);
    check(hit.length === 0, `split: nenhum texto cobre a legenda (y ${cap.top.toFixed(0)}-${cap.bottom})`
      + (hit.length ? ` cobre: ${JSON.stringify(hit[0])}` : ""));
    const hits = (x, y) => x.left < y.right - 2 && y.left < x.right - 2 && x.top < y.bottom - 2 && y.top < x.bottom - 2;
    check(!boxes.some((x, i) => boxes.slice(i + 1).some((y) => hits(x, y))), "split: faixas sem sobreposição de texto");
    const pr = (probe.presenters ?? [])[0];
    check(!!pr, "split: apresentador presente");
    if (pr) {
      check(pr.top >= SAFE.top && pr.bottom <= SAFE.bottom && pr.right <= WIDTH - SAFE.rightGuard + 0.5 && pr.left >= 0,
        `split: apresentador na zona segura (y ${pr.top.toFixed(0)}-${pr.bottom.toFixed(0)})`);
      check(!boxes.some((b) => hits(b, pr)), "split: apresentador sem sobrepor texto");
    }
    check(probe.minSize >= 44, `split: menor texto ${probe.minSize}px >= 44px`);
  }
  if (want("cta")) {
    const texts = ["Quer ver mais?", "Siga para ver mais sobre automação local de vídeo ok",
      "Rode npx @nathanramorim/forge-sdd init e comece agora ok"];
    const lonely = (lines) => lines.some((l) => l.length > 1 && l.at(-1) < 2);
    for (const text of texts) {
      const scene = { type: "cta", dur: 3, narration: "", text };
      const forgeProps = { ...engineProps([scene], theme.id, forge.id), probe: true };
      const { probe } = await probeAt(forgeProps, 85);
      const lines = (probe.ctaLines ?? [])[0] ?? [];
      check(lines.length > 0 && !lonely([lines]), `cta forge-motion "${text.slice(0, 24)}": linhas ${JSON.stringify(lines)} sem palavra sozinha`);
      const props = { ...overlayProps([{ at: 0, dur: 6, type: "cta", text }], 6), probe: true };
      const composition = await selectComposition({ serveUrl, id: "Overlay", inputProps: props });
      const logs = [];
      await renderStill({ composition, serveUrl, output: path.join(tmp, "cta.png"), inputProps: props, frame: 90,
        imageFormat: "png", onBrowserLog: (l) => logs.push(l.text) });
      const ov = JSON.parse((logs.find((t) => t.startsWith("[probe]")) ?? "[probe] {}").slice(8));
      const ovLines = (ov.ctaLines ?? [])[0] ?? [];
      check(ovLines.length > 0 && !lonely([ovLines]), `cta overlay "${text.slice(0, 24)}": linhas ${JSON.stringify(ovLines)} sem palavra sozinha`);
    }
  }
  if (want("transitions")) {
    // Os limites vêm de render/src/timeline.ts (DUP-03): o script lê a duração, sem cópia.
    const seconds = Number(/TRANSITION_SECONDS = ([\d.]+)/.exec(readFileSync(path.join(root, "src/timeline.ts"), "utf8"))[1]);
    const half = Math.max(1, Math.round((seconds / 2) * 30)), end = 90;
    const frames = [end - half, end - Math.ceil(half / 2), end - 1, end, end + Math.floor(half / 2), end + half - 1];
    for (const kind of ["dip", "wipe", "slide"]) {
      const scenes = [
        { type: "title", dur: 3, narration: "", text: "Primeira cena do reel", transition: kind },
        { type: "highlight", dur: 3, narration: "", text: "Segunda cena do reel" },
      ];
      const inputProps = { ...engineProps(scenes, theme.id, forge.id), probe: true };
      let worst = 0, overlap = false, gap = 0;
      for (const frame of frames) {
        const { probe } = await probeAt(inputProps, frame);
        const boxes = (probe.boxes ?? []).filter((b) => b.presence !== undefined);
        const byScene = new Map();
        for (const b of boxes) byScene.set(b.scene, Math.max(byScene.get(b.scene) ?? 0, b.presence));
        worst = Math.max(worst, [...byScene.values()].reduce((a, v) => a + v, 0));
        const seen = boxes.filter((b) => b.presence > 0.05);
        const hits = (x, y) => x.left < y.right - 2 && y.left < x.right - 2 && x.top < y.bottom - 2 && y.top < x.bottom - 2;
        overlap ||= seen.some((x, i) => seen.slice(i + 1).some((y) => x.scene !== y.scene && hits(x, y)));
        if (frame === end - 1 || frame === end) gap = Math.max(gap, ...[...byScene.values(), 0]);
      }
      check(worst <= 1.05, `transição ${kind}: soma das presenças ${worst.toFixed(2)} <= 1.05 (sem dupla exposição)`);
      check(!overlap, `transição ${kind}: texto de cenas diferentes sem sobreposição`);
      check(gap <= 0.1, `transição ${kind}: passa pelo fundo entre as cenas (presença ${gap.toFixed(2)} <= 0.1)`);
    }
  }
  if (want("words")) {
    const words = (texts, start, step) => texts.flatMap((w, k) => [{ word: w, start: start + k * step, end: start + (k + 1) * step }]);
    const cases = [
      { type: "title", dur: 4, narration: "", text: "Automatize esse processo de ponta a ponta",
        words: words(["Automatize", "esse", "processo", "de", "ponta", "a", "ponta"], 0.5, 0.3) },
      { type: "list", dur: 4, narration: "", items: ["Sem nuvem", "Sem custo", "Controle total"],
        words: words(["Sem", "nuvem", "custo", "controle", "total"], 0.5, 0.4) },
    ];
    for (const scene of cases) {
      const inputProps = { ...engineProps([{ ...scene, words: undefined }], theme.id, forge.id), probe: true };
      inputProps.scenes[0].words = scene.words;
      let early = 0, late = 0, total = 0;
      for (const frame of [12, 27, 60, Math.round(scene.dur * 30) - 5]) {
        const t = frame / 30;
        const { probe } = await probeAt(inputProps, frame);
        for (const r of probe.reveals ?? []) {
          total += 1;
          if (t < r.at && r.opacity > 0.02) early += 1;
          if (t >= r.at + 1.0 && r.opacity < 0.95) late += 1;
        }
      }
      check(total > 0, `${scene.type}: palavras marcadas para revelar (${total} leituras)`);
      check(early === 0, `${scene.type}: nenhuma palavra visível antes do seu tempo`);
      check(late === 0, `${scene.type}: todas visíveis depois do seu tempo`);
    }
  }
  if (want("media")) {
    const pub = path.join(tmp, "public");
    mkdirSync(pub);
    for (const f of readdirSync(path.join(root, "public"))) symlinkSync(path.join(root, "public", f), path.join(pub, f));
    const made = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=duration=3:size=640x360:rate=30",
      "-pix_fmt", "yuv420p", path.join(pub, "clip.mp4")], { encoding: "utf8" });
    check(made.status === 0, "ffmpeg gerou o vídeo de teste");
    const url = await bundle({ entryPoint: path.join(root, "src/index.ts"), publicDir: pub });
    const scene = { type: "highlight", dur: 3, narration: "", text: "Tela real dentro da janela" };
    const inputProps = { ...engineProps([scene], theme.id, forge.id), probe: true };
    inputProps.scenes[0].media = { file: "clip.mp4", start: 0, end: 3, region: { x: 0, y: 0, w: 1, h: 1 } };
    const { probe, output } = await probeAt(inputProps, 45, url);
    const box = (probe.media ?? [])[0];
    check(!!box, "media: janela com a tela real presente");
    if (box) {
      check(box.top >= SAFE.top && box.bottom <= SAFE.bottom && box.right <= WIDTH - SAFE.rightGuard + 0.5,
        `media: janela na zona segura (y ${box.top.toFixed(0)}-${box.bottom.toFixed(0)})`);
      const img = decodePng(readFileSync(output));
      const px = (x, y) => [0, 1, 2].map((k) => img.px[(Math.round(y) * img.w + Math.round(x)) * img.ch + k]);
      const far = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) > 40;
      const samples = [0.2, 0.5, 0.8].map((f) => px(box.left + (box.right - box.left) * f, box.top + (box.bottom - box.top) * 0.5));
      check(samples.some((c) => far(c, hex(theme.colors.bg)) && far(c, hex(theme.colors.surface))),
        "media: a tela real aparece dentro da janela (pixels do vídeo, não do fundo)");
    }
    const { probe: p2 } = await probeAt({ ...engineProps([scene], theme.id, forge.id), probe: true }, 45);
    check((p2.media ?? []).length === 0, "media: cena sem `media` não mostra janela de vídeo");
  }
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
if (failures.length) { console.error(`\n${failures.length} verificação(ões) falharam`); process.exit(1); }
console.log("\ntudo ok");
