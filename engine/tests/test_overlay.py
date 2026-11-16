"""Camada de componentes sobre o corte (05-04): corte intacto, passo extra, dry-run sem escrita."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from reel_studio import cli
from reel_studio.core import overlay
from reel_studio.core.contracts import load_theme
from reel_studio.core.cut import plan
from reel_studio.core.errors import ReelError

OVERLAYS = [{"at": 0.5, "dur": 2.0, "type": "hook", "text": "Gancho"},
            {"at": 1.0, "dur": 1.5, "type": "cta", "text": "npx forge"}]


def _jobs(tmp_path, transcript, overlays=True, with_overlays=True):
    clip = {"id": "clip-01", "start": 10.0, "end": 14.0, "hook": "x"}
    if with_overlays:
        clip["overlays"] = OVERLAYS
    return plan(Path("v.mp4"), tmp_path, {"clips": [clip]}, transcript, load_theme("forge"),
                size=(1080, 1920), overlays=overlays)


def test_regressao_comando_do_corte_nao_muda_com_camadas(tmp_path, transcript):
    sem = _jobs(tmp_path, transcript, with_overlays=False)[0]
    com = _jobs(tmp_path, transcript)[0]
    assert com.args == sem.args and com.out == sem.out
    # 05-13: o overlay `hook` já desenha o gancho, então o `.ass` não o repete.
    assert "Dialogue: 1" in sem.ass_text and "Dialogue: 1" not in com.ass_text
    assert com.ass_text == sem.ass_text.replace(
        next(ln for ln in sem.ass_text.splitlines() if ln.startswith("Dialogue: 1")) + "\n", "")


def test_regressao_sem_camadas_nao_ha_passo_de_composicao(tmp_path, transcript):
    assert overlay.plan(_jobs(tmp_path, transcript, with_overlays=False), tmp_path) == []


def test_regressao_com_camadas_ha_um_passo_a_mais(tmp_path, transcript):
    layers = overlay.plan(_jobs(tmp_path, transcript), tmp_path)
    assert len(layers) == 1 and layers[0].count == 2
    assert layers[0].compose_args[0] == "ffmpeg" and "overlay" in " ".join(
        layers[0].compose_args)


def test_overlays_none_gera_o_mesmo_plano_que_sem_camadas(tmp_path, transcript):
    none = _jobs(tmp_path, transcript, overlays=False)
    assert none == _jobs(tmp_path, transcript, with_overlays=False)
    assert overlay.plan(none, tmp_path) == []


def test_camada_dura_o_mesmo_que_o_corte_e_desloca_pela_folga(tmp_path, transcript):
    job = _jobs(tmp_path, transcript)[0]
    layer = overlay.plan([job], tmp_path)[0]
    assert layer.length == pytest.approx(job.end - job.start)
    assert job.overlays[0]["at"] == pytest.approx(0.5 + (10.0 - job.start))
    assert job.start < 10.0


def test_camada_usa_alfa_e_formato_de_composicao(tmp_path, transcript):
    layer = overlay.plan(_jobs(tmp_path, transcript), tmp_path)[0]
    cmd = layer.render_args
    assert "Overlay" in cmd and "--codec=prores" in cmd and "--prores-profile=4444" in cmd
    assert "--pixel-format=yuva444p10le" in cmd and "--image-format=png" in cmd
    assert layer.out.name == "clip-01-forge-overlay.mp4"
    assert all(";" not in a and "&&" not in a for a in layer.render_args + layer.compose_args)


def test_camada_remove_intermediarios_mesmo_com_falha(tmp_path, transcript, monkeypatch):
    jobs = _jobs(tmp_path, transcript)
    layers = overlay.plan(jobs, tmp_path)
    rdir = tmp_path / "render"
    (rdir / "node_modules").mkdir(parents=True)
    monkeypatch.setattr(overlay.paths, "render_dir", lambda: rdir)
    monkeypatch.setattr(overlay.proc, "require_bin", lambda n, _h: n)

    def fake_run(args, cwd=None):
        if "remotion" in args:
            layers[0].layer.write_bytes(b"x")
        else:
            raise ReelError("composição falhou")

    monkeypatch.setattr(overlay.proc, "run", fake_run)
    with pytest.raises(ReelError, match="composição"):
        overlay.execute(layers, jobs, load_theme("forge"), tmp_path)
    assert not layers[0].layer.exists() and not layers[0].props_file.exists()


def test_props_da_camada_trazem_tema_e_logo_como_data_uri(tmp_path, transcript):
    job = _jobs(tmp_path, transcript)[0]
    props = overlay.layer_props(job, load_theme("forge"))
    assert props["length"] == pytest.approx(job.end - job.start)
    assert props["theme"]["brand"]["logoUri"].startswith("data:image/svg+xml;base64,")
    assert "logo" not in props["theme"]["brand"]
    assert props["style"]["id"] == "forge-motion"


def test_tema_sem_brand_continua_gerando_props(tmp_path, transcript):
    job = _jobs(tmp_path, transcript)[0]
    props = overlay.layer_props(job, load_theme("exemplo"))
    assert "brand" not in props["theme"]


def test_modo_invalido_e_rejeitado():
    with pytest.raises(ReelError, match="--overlays"):
        overlay.validate_mode("sim")


def test_cut_dry_run_nao_escreve_nada(tmp_path, monkeypatch, transcript):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    (tmp_path / "v.reel").mkdir()
    clip = {"id": "clip-01", "start": 10.0, "end": 14.0, "hook": "x", "overlays": OVERLAYS}
    (tmp_path / "v.reel" / "clips.json").write_text(json.dumps({"clips": [clip]}))
    monkeypatch.setattr(cli, "_corrected", lambda *_a, **_k: (transcript, ""))
    monkeypatch.setattr(cli.cut.proc, "probe_size", lambda _v: (1080, 1920))

    class P:
        def __init__(self):
            self.video, self.dir = video, tmp_path / "v.reel"

        def require(self, name, _hint):
            return self.dir / name

    monkeypatch.setattr(cli.Project, "open", lambda _v: P())
    before = sorted(p.name for p in tmp_path.rglob("*"))
    res = CliRunner().invoke(cli.app, ["cut", str(video), "--theme", "forge", "--dry-run"])
    assert res.exit_code == 0, res.output
    assert "camada de 2 componentes" in res.output
    assert sorted(p.name for p in tmp_path.rglob("*")) == before
    none = CliRunner().invoke(cli.app, ["cut", str(video), "--theme", "forge", "--dry-run",
                                        "--overlays", "none"])
    assert "camada" not in none.output


def test_camada_entrega_poster_no_quadro_0(tmp_path, transcript, monkeypatch):
    jobs = _jobs(tmp_path, transcript)
    layers = overlay.plan(jobs, tmp_path)
    rdir = tmp_path / "render"
    (rdir / "node_modules").mkdir(parents=True)
    monkeypatch.setattr(overlay.paths, "render_dir", lambda: rdir)
    monkeypatch.setattr(overlay.proc, "require_bin", lambda n, _h: n)
    chamadas = []

    def fake_run(args, cwd=None):
        chamadas.append(args)
        for arg in args:
            if str(arg).endswith(".poster.mp4"):
                overlay.Path(arg).write_bytes(b"x")

    monkeypatch.setattr(overlay.proc, "run", fake_run)
    monkeypatch.setattr(overlay.deliver.proc, "run", fake_run)
    layers[0].out.parent.mkdir(parents=True, exist_ok=True)
    layers[0].out.write_bytes(b"x")
    overlay.execute(layers, jobs, load_theme("forge"), tmp_path)
    juntas = [" ".join(map(str, c)) for c in chamadas]
    assert any("-frames:v" in c and "-poster.jpg" in c for c in juntas)
    assert any("overlay=enable='eq(n,0)'" in c for c in juntas)


def test_moldura_rente_ao_video_no_fit_e_ausente_no_fill():
    from reel_studio.core.cut import Layout, video_rect
    rect = video_rect(Layout(kind="fit"), (2860, 1776))
    assert rect["left"] == 0 and rect["width"] == 1080 and rect["height"] < 920
    assert rect["top"] == 320 + (920 - rect["height"]) // 2
    quadrado = video_rect(Layout(kind="fit"), (1000, 1000))
    assert quadrado["width"] == 920 and quadrado["left"] == 80 and quadrado["top"] == 320
    assert video_rect(Layout(kind="fill"), (1920, 1080)) is None


def test_layer_props_leva_o_retangulo_do_video(tmp_path, transcript):
    from reel_studio.core.cut import Layout
    job = _jobs(tmp_path, transcript)[0]
    assert overlay.layer_props(job, load_theme("forge"))["frame"] is None
    fit = type(job)(**{**job.__dict__, "layout": Layout(kind="fit"), "size": (2860, 1776)})
    assert overlay.layer_props(fit, load_theme("forge"))["frame"]["width"] == 1080


# --- 05-14: corte dividido, abertura e apresentador ---
def _split_job(tmp_path, transcript, **extra):
    clip = {"id": "clip-01", "start": 10.0, "end": 14.0, "hook": "Gancho", **extra}
    return plan(Path("v.mp4"), tmp_path, {"clips": [clip]}, transcript, load_theme("forge"),
                size=(2860, 1776))[0]


def test_split_retangulo_na_faixa_de_cima():
    from reel_studio.core.cut import Layout, video_rect
    rect = video_rect(Layout(kind="split"), (2860, 1776))
    assert rect["top"] >= 250 and rect["top"] + rect["height"] <= 950 and rect["width"] <= 1080
    assert video_rect(Layout(kind="fit"), (2860, 1776))["top"] == 445  # fit não muda


def test_split_filtro_usa_a_faixa_de_cima_e_o_fit_nao_muda():
    from reel_studio.core.cut import Layout, video_filter
    split = video_filter(Layout(kind="split"), (2860, 1776), "a.ass", "#0a0e1a")
    assert "scale=1080:700" in split and ":250+(700-ih)/2" in split
    fit = video_filter(Layout(kind="fit"), (2860, 1776), "a.ass", "#0a0e1a")
    assert "scale=1080:920" in fit and ":320+(920-ih)/2" in fit


def test_split_pelo_clips_json_e_cli_vence(tmp_path, transcript):
    assert _split_job(tmp_path, transcript, layout="split").layout.kind == "split"
    clip = {"id": "clip-01", "start": 10.0, "end": 14.0, "layout": "split"}
    job = plan(Path("v.mp4"), tmp_path, {"clips": [clip]}, transcript, load_theme("forge"),
               size=(2860, 1776), layout="fit")[0]
    assert job.layout.kind == "fit"


def test_split_contrato_aceita_e_rejeita():
    import pytest

    from reel_studio.core import contracts
    from reel_studio.core.errors import ContractError
    ok = {"clips": [{"id": "clip-01", "start": 1.0, "end": 9.0, "hook": "x", "layout": "split",
                     "presenter": True, "intro": {"dur": 1.5, "text": "Oi"}}]}
    assert contracts.validate("clips", ok)
    for bad in ({"layout": "dividido"}, {"presenter": "sim"}, {"intro": {"dur": 9}},
                {"intro": {"dur": 1, "x": 1}}):
        with pytest.raises(ContractError):
            contracts.validate("clips", {"clips": [{"id": "clip-01", "start": 1.0, "end": 9.0,
                                                    "hook": "x", **bad}]})


def test_intro_adiciona_passo_de_concatenacao(tmp_path, transcript):
    job = _split_job(tmp_path, transcript, intro={"dur": 1.5})
    steps = overlay.plan([job], tmp_path)
    assert len(steps) == 1 and steps[0].render_args == [] and steps[0].intro
    intro = steps[0].intro
    assert intro.dur == 1.5 and intro.out.name.endswith("-abertura.mp4")
    assert "concat=n=2:v=1:a=1" in " ".join(intro.concat_args)
    assert intro.concat_args[-1] == str(intro.out)
    assert job.args == _split_job(tmp_path, transcript).args  # o corte não muda


def test_intro_com_camada_concatena_a_saida_da_camada(tmp_path, transcript):
    job = _split_job(tmp_path, transcript, intro={}, overlays=[
        {"at": 0.5, "dur": 1.0, "type": "hook", "text": "x"}])
    step = overlay.plan([job], tmp_path)[0]
    assert step.render_args and step.intro.source == step.out
    assert step.intro.dur == overlay.INTRO_SECONDS


def test_intro_dry_run_nao_escreve(tmp_path, transcript):
    job = _split_job(tmp_path, transcript, intro={"dur": 1.0}, presenter=True)
    overlay.plan([job], tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_apresentador_exige_camada_e_leva_a_fala(tmp_path, transcript):
    job = _split_job(tmp_path, transcript, presenter=True)
    step = overlay.plan([job], tmp_path)[0]
    assert step.render_args and step.count == 0
    props = overlay.layer_props(job, load_theme("forge"))
    assert props["presenter"] is True and props["layout"] == "fit"
    assert all(0 <= a < b for a, b in job.speech)


def test_sem_split_intro_e_presenter_nada_muda(tmp_path, transcript):
    job = _split_job(tmp_path, transcript)
    assert overlay.plan([job], tmp_path) == [] and job.speech == ()
