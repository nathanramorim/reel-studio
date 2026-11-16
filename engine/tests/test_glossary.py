import json
import re
from pathlib import Path

import pytest

from reel_studio.cli import app
from reel_studio.core import glossary
from reel_studio.core.captions import build_ass
from reel_studio.core.contracts import load_theme
from reel_studio.core.errors import ReelError


def _t(*words: str) -> dict:
    ws, t = [], 0.0
    for w in words:
        ws.append({"start": t, "end": t + 1.0, "word": w})
        t += 1.0
    return {"language": "pt", "duration": t,
            "segments": [{"start": 0.0, "end": t, "text": " ".join(words), "words": ws}]}


RELATO = {"Forge STD": "Forge SDD", "fitres": "features", "Plane": "Plan",
          "QEJ-Zone": "queue.json", "assete": "aceite"}


@pytest.mark.parametrize("errado,certo", [
    (("o", "Forge", "STD"), "o Forge SDD"),
    (("as", "fitres"), "as features"),
    (("o", "Plane"), "o Plan"),
    (("ver", "QEJ", "-Zone"), "ver queue.json"),
    (("o", "assete"), "o aceite"),
])
def test_corrige_os_casos_do_relato(errado, certo):
    out, n = glossary.apply(_t(*errado), RELATO)
    seg = out["segments"][0]
    assert n == 1
    assert seg["text"] == certo
    assert " ".join(w["word"] for w in seg["words"]) == certo


def test_duas_palavras_por_uma_mantem_tempos():
    out, _ = glossary.apply(_t("a", "Forge", "STD", "b"), {"Forge STD": "Forge"})
    ws = out["segments"][0]["words"]
    assert [w["word"] for w in ws] == ["a", "Forge", "b"]
    assert (ws[1]["start"], ws[1]["end"]) == (1.0, 3.0)


def test_uma_palavra_por_duas_divide_o_intervalo_sem_sobrepor():
    out, _ = glossary.apply(_t("a", "fitres", "b"), {"fitres": "fi tres"})
    ws = out["segments"][0]["words"]
    assert [w["word"] for w in ws] == ["a", "fi", "tres", "b"]
    assert ws[1]["start"] == 1.0 and ws[2]["end"] == 2.0
    assert ws[1]["end"] == ws[2]["start"]
    assert ws[1]["end"] < ws[2]["end"]


def test_ignora_caixa_e_pontuacao_e_preserva_a_final():
    out, n = glossary.apply(_t("o", "PLANE."), {"plane": "Plan"})
    assert n == 1
    assert out["segments"][0]["words"][1]["word"] == "Plan."
    assert out["segments"][0]["text"] == "o Plan."


def test_nao_reaplica_sobre_si_mesma_e_nao_muda_o_original():
    t = _t("a", "x")
    out, _ = glossary.apply(t, {"x": "x x", "x x": "y"})
    assert [w["word"] for w in out["segments"][0]["words"]] == ["a", "x", "x"]
    assert t["segments"][0]["words"][1]["word"] == "x"


def test_frase_mais_longa_vence():
    out, _ = glossary.apply(_t("Forge", "STD"), {"Forge": "F", "Forge STD": "Forge SDD"})
    assert out["segments"][0]["text"] == "Forge SDD"


def _write(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_precedencia_explicito_pasta_e_tema(tmp_path):
    (tmp_path / ".git").mkdir()
    video = tmp_path / "gravacoes" / "v.mov"
    video.parent.mkdir()
    work = tmp_path / "work"
    work.mkdir()
    theme = {"id": "t", "glossary": {"a": "tema"}}
    assert glossary.find(video, work, theme).mapping == {"a": "tema"}
    _write(work / "correcoes.json", {"a": "trabalho"})
    assert glossary.find(video, work, theme).mapping == {"a": "trabalho"}
    _write(tmp_path / "correcoes.json", {"a": "raiz"})
    assert glossary.find(video, work, theme).mapping == {"a": "raiz"}
    _write(video.parent / "correcoes.json", {"_nota": "x", "a": "pasta"})
    assert glossary.find(video, work, theme).mapping == {"a": "pasta"}
    ex = _write(tmp_path / "outro.json", {"a": "explicito"})
    assert glossary.find(video, work, theme, ex).mapping == {"a": "explicito"}


def test_sem_glossario_devolve_none(tmp_path):
    (tmp_path / ".git").mkdir()
    video = tmp_path / "v.mov"
    assert glossary.find(video, tmp_path / "w", {}) is None


@pytest.mark.parametrize("conteudo", ["[1]", "{", '{"a": 1}'])
def test_arquivo_invalido_e_rejeitado(tmp_path, conteudo):
    f = tmp_path / "correcoes.json"
    f.write_text(conteudo)
    with pytest.raises(ReelError, match="correcoes.json"):
        glossary.load(f)


def test_arquivo_grande_demais_e_rejeitado(tmp_path):
    f = tmp_path / "correcoes.json"
    f.write_text(json.dumps({"k": "x" * (glossary.MAX_BYTES + 1)}))
    with pytest.raises(ReelError, match="grande demais"):
        glossary.load(f)


def test_entradas_demais_sao_rejeitadas(tmp_path):
    f = _write(tmp_path / "correcoes.json",
               {f"k{i}": "v" for i in range(glossary.MAX_ENTRIES + 1)})
    with pytest.raises(ReelError, match="entradas"):
        glossary.load(f)


def test_glossario_chega_na_legenda():
    out, _ = glossary.apply(_t("o", "Forge", "STD"), RELATO)
    ass = re.sub(r"\{[^}]*\}", "", build_ass(out, 0.0, 3.0, load_theme("forge")))
    assert "SDD" in ass and "STD" not in ass


def test_cut_dry_run_informa_glossario_e_nao_escreve(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    (tmp_path / ".git").mkdir()
    video = tmp_path / "v.mov"
    video.write_bytes(b"x")
    _write(tmp_path / "correcoes.json", {"fitres": "features"})
    monkeypatch.setattr("reel_studio.core.proc.probe_size", lambda _v: (1080, 1920))
    from reel_studio.core.project import Project
    p = Project.open(video)
    _write(p.path("transcript.json"), _t("as", "fitres"))
    clip = {"id": "clip-01", "start": 0.0, "end": 2.0, "hook": "x"}
    _write(p.path("clips.json"), {"clips": [clip]})
    before = sorted(x.name for x in tmp_path.rglob("*"))
    res = CliRunner().invoke(app, ["cut", str(video), "--theme", "forge", "--dry-run"])
    assert res.exit_code == 0, res.output
    assert "glossário: 1 correções" in res.output
    assert sorted(x.name for x in tmp_path.rglob("*")) == before
    assert json.loads(p.path("transcript.json").read_text())["segments"][0]["text"] == "as fitres"
