"""Legenda .ass no visual do tema (palavra em destaque ou linha simples)."""

from __future__ import annotations

W, H = 1080, 1920
CHUNK_WORDS = 3
CHUNK_SECONDS = 1.4
MARGIN_V = {"bottom": 220, "lower-third": 560, "center": 0}
ALIGN = {"bottom": 2, "lower-third": 2, "center": 5}


def ass_color(hex_color: str, alpha: int = 0) -> str:
    """#RRGGBB para &HAABBGGRR (formato do ASS)."""
    r, g, b = hex_color[1:3], hex_color[3:5], hex_color[5:7]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    cs = round(seconds * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _escape(text: str) -> str:
    return text.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", " ")


def words_in(transcript: dict, start: float, end: float) -> list[dict]:
    out = []
    for seg in transcript["segments"]:
        default = [{"start": seg["start"], "end": seg["end"], "word": seg["text"]}]
        words = seg.get("words") or default
        for w in words:
            if w["start"] >= start and w["end"] <= end + 0.05 and w["word"].strip():
                out.append({"start": w["start"] - start, "end": w["end"] - start,
                            "word": w["word"].strip()})
    return out


def chunk(words: list[dict]) -> list[list[dict]]:
    chunks: list[list[dict]] = []
    for w in words:
        if (chunks and len(chunks[-1]) < CHUNK_WORDS
                and w["end"] - chunks[-1][0]["start"] <= CHUNK_SECONDS):
            chunks[-1].append(w)
        else:
            chunks.append([w])
    return chunks


def header(theme: dict) -> str:
    c, cap = theme["colors"], theme["caption"]
    pos = cap["position"]
    size = cap.get("size", 72)
    font = theme["fonts"]["title"]
    outline = ass_color(c["bg"], 0x20)
    return "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,{font},{size},{ass_color(c['text'])},{ass_color(c['accent'])},"
        f"{outline},{outline},-1,0,0,0,100,100,0,0,1,6,0,{ALIGN[pos]},80,80,{MARGIN_V[pos]},1",
        f"Style: Hook,{font},{int(size * 0.8)},{ass_color(c['bg'])},{ass_color(c['bg'])},"
        f"{ass_color(c['accent'])},{ass_color(c['accent'])},-1,0,0,0,100,100,0,0,3,24,0,8,80,80,180,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ])


def build_ass(transcript: dict, start: float, end: float, theme: dict, hook: str = "") -> str:
    cap = theme["caption"]
    accent = ass_color(theme["colors"]["accent"])
    upper = cap.get("uppercase", False)
    lines = [header(theme)]
    if hook:
        hook_end = ts(min(4.0, end - start))
        lines.append(f"Dialogue: 1,{ts(0)},{hook_end},Hook,,0,0,0,,{_escape(hook)}")
    for group in chunk(words_in(transcript, start, end)):
        texts = [_escape(w["word"].upper() if upper else w["word"]) for w in group]
        g_end = group[-1]["end"]
        if cap["style"] == "line":
            lines.append(f"Dialogue: 0,{ts(group[0]['start'])},{ts(g_end)},Caption,,0,0,0,,"
                         + " ".join(texts))
            continue
        for i, w in enumerate(group):
            w_end = group[i + 1]["start"] if i + 1 < len(group) else g_end
            parts = [f"{{\\c{accent}}}{t}{{\\r}}" if j == i else t for j, t in enumerate(texts)]
            lines.append(f"Dialogue: 0,{ts(w['start'])},{ts(w_end)},Caption,,0,0,0,,"
                         + " ".join(parts))
    return "\n".join(lines) + "\n"
