// Verifica stills de cada cena: fonte carregada, escala mínima, cobertura e paleta.
// Uso: node scripts/check-render.mjs [--fonts] [--scale] [--style <id>]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { readFileSync, mkdtempSync, rmSync } from "node:fs";
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
const all = !flag("fonts") && !flag("scale") && !styleId;
const readJson = (p) => JSON.parse(readFileSync(p, "utf8"));

const theme = readJson(path.join(repo, "themes/forge.json"));
const SCENES = [
  { type: "title", dur: 3, narration: "", text: "Automatize esse processo de ponta a ponta" },
  { type: "highlight", dur: 3, narration: "", text: "Tudo roda local, sem enviar nada" },
  { type: "flow", dur: 5, narration: "", steps: ["Extrair áudio", "Transcrever local", "Escolher trechos", "Gerar reel"] },
  { type: "list", dur: 4, narration: "", items: ["Sem nuvem", "Sem custo por minuto", "Controle total"] },
  { type: "compare", dur: 4, narration: "",
    left: { label: "Antes", points: ["Edição manual", "Horas por vídeo"] },
    right: { label: "Depois", points: ["Pipeline local", "Minutos por vídeo"] } },
  { type: "cta", dur: 3, narration: "", text: "Quer ver mais?" },
];
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
  for (const sid of all ? ["__default__", ...STYLES.slice(0, 1)] : styleId ? [styleId] : ["__default__"]) {
    const style = sid === "__default__" ? readJson(path.join(repo, "styles", STYLES[2], "style.json")) : readJson(path.join(repo, "styles", sid, "style.json"));
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
      if (all || flag("fonts")) {
        check(!logs.some((t) => t.includes("[font-fallback]")), `${tag}: sem fallback de fonte`);
        check((probe.fonts ?? []).length > 0 && probe.fonts.every((f) => f.loaded && f.width !== f.serifWidth),
          `${tag}: texto em ${(probe.fonts ?? []).map((f) => f.family).join("+")} (largura difere da serifa)`);
      }
      if (all || flag("scale")) {
        check(probe.minSize >= 44, `${tag}: menor texto ${probe.minSize}px >= 44px`);
      }
      if (all || styleId) {
        const palette = [...inputProps.style.look.palette.map(hex), hex(theme.colors.accent)];
        const a = analyze(decodePng(readFileSync(out)), hex(theme.colors.bg), palette);
        if (style.id === "isometric-pastel") {
          if (scene.type === "flow") check(a.coverage >= 0.7, `${tag}: cobertura vertical ${(a.coverage * 100).toFixed(0)}% >= 70%`);
          check(a.gap <= 0.25, `${tag}: maior faixa vazia ${(a.gap * 100).toFixed(0)}% <= 25%`);
          check(a.corner.every((v, k) => Math.abs(v - hex(theme.colors.bg)[k]) <= 8), `${tag}: fundo do tema ${theme.id}`);
          check(a.colors >= 3, `${tag}: ${a.colors} cores da paleta (>= 3)`);
        }
      }
    }
  }
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
if (failures.length) { console.error(`\n${failures.length} verificação(ões) falharam`); process.exit(1); }
console.log("\ntudo ok");
