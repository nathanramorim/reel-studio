from pathlib import Path

from reel_studio.core.contracts import load_theme
from reel_studio.core.cut import ffmpeg_args, plan


def test_ffmpeg_args_corta_e_aplica_legenda():
    args = ffmpeg_args("ffmpeg", Path("v.mp4"), 1.0, 4.0, "clip-01.ass", Path("out.mp4"))
    assert "-ss" in args and "1.00" in args
    assert "-t" in args and "3.00" in args
    assert any("ass=clip-01.ass" in a for a in args)
    assert all(";" not in a and "&&" not in a for a in args)


def test_plan_gera_um_job_por_clip(tmp_path, transcript):
    clips = {"clips": [{"id": "clip-01", "start": 0.0, "end": 3.2, "hook": "x"}]}
    jobs = plan(Path("v.mp4"), tmp_path, clips, transcript, load_theme("pessoal"),
                size=(1080, 1920))
    assert len(jobs) == 1
    assert jobs[0].out.name == "clip-01-pessoal.mp4"


# --- layout automático ---
import pytest  # noqa: E402

from reel_studio.cli import app  # noqa: E402
from reel_studio.core.cut import Layout, choose_layout, parse_anchor, video_filter  # noqa: E402
from reel_studio.core.errors import ReelError  # noqa: E402
from reel_studio.core.frames import Analysis, Region  # noqa: E402

TELA = (2860, 1776)


def test_layout_em_pe_usa_fill():
    assert choose_layout((1080, 1920), None).kind == "fill"


def test_layout_paisagem_sem_opencv_usa_fit():
    assert choose_layout(TELA, None).kind == "fit"


def test_layout_paisagem_sem_rosto_e_sem_atividade_usa_fit():
    assert choose_layout(TELA, Analysis()).kind == "fit"


def test_layout_rosto_centraliza_o_fill():
    esq = choose_layout(TELA, Analysis(face_x=0.2))
    dir_ = choose_layout(TELA, Analysis(face_x=0.8))
    assert esq.kind == dir_.kind == "fill"
    assert esq.anchor < 0.5 < dir_.anchor


def test_layout_atividade_concentrada_usa_zoom():
    lay = choose_layout(TELA, Analysis(region=Region(0.1, 0.5, 0.5, 0.3)))
    assert lay.kind == "zoom"
    vf = video_filter(lay, TELA, "c.ass")
    assert "crop=" in vf and "boxblur" not in vf and "ass=c.ass" in vf


def test_layout_fit_nao_corta_o_video_principal():
    vf = video_filter(Layout("fit"), TELA, "c.ass")
    assert "crop" not in vf and "boxblur" not in vf and "pad=1080:1920" in vf


def test_layout_plan_escolhe_sem_parametro(tmp_path, transcript):
    clips = {"clips": [{"id": "clip-01", "start": 0.0, "end": 3.2}]}
    jobs = plan(Path("v.mov"), tmp_path, clips, transcript, load_theme("pessoal"),
                size=TELA, analyzer=lambda *_: None)
    assert jobs[0].layout.kind == "fit"
    assert "-vf" in jobs[0].args and "-filter_complex" not in jobs[0].args


def test_anchor_left_e_right_mudam_o_x_do_crop():
    esq = video_filter(Layout("fill", anchor=parse_anchor("left")), TELA, "c.ass")
    dir_ = video_filter(Layout("fill", anchor=parse_anchor("right")), TELA, "c.ass")
    assert esq != dir_ and "(iw-1080)*0.0000" in esq and "(iw-1080)*1.0000" in dir_


@pytest.mark.parametrize("valor", ["1.5", "-0.1", "abc"])
def test_anchor_invalido_e_rejeitado(valor):
    with pytest.raises(ReelError):
        parse_anchor(valor)


def test_anchor_invalido_no_plan(tmp_path, transcript):
    clips = {"clips": [{"id": "clip-01", "start": 0.0, "end": 3.2}]}
    with pytest.raises(ReelError):
        plan(Path("v.mov"), tmp_path, clips, transcript, load_theme("pessoal"),
             size=TELA, anchor=2.0)


def test_layout_invalido_e_rejeitado(tmp_path, transcript):
    with pytest.raises(ReelError):
        plan(Path("v.mov"), tmp_path, {"clips": []}, transcript, load_theme("pessoal"),
             size=TELA, layout="x")


def test_frames_sem_opencv_devolve_none(monkeypatch):
    import builtins

    from reel_studio.core import frames
    real = builtins.__import__

    def fake(name, *a, **k):
        if name == "cv2":
            raise ImportError
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake)
    assert frames.analyze(Path("v.mov"), 0, 1) is None


def test_dry_run_mostra_layout_e_nao_escreve(tmp_path, monkeypatch, transcript):
    from typer.testing import CliRunner

    video = tmp_path / "v.mov"
    video.write_bytes(b"x")
    monkeypatch.setattr(cutmod.proc, "probe_size", lambda _v: TELA)
    monkeypatch.setattr(cutmod.frames, "analyze", lambda *_: None)
    from reel_studio import cli
    monkeypatch.setattr(cli.Project, "open", lambda v: _FakeProject(video, tmp_path, transcript))
    real_load = cli.contracts.load
    monkeypatch.setattr(
        cli.contracts, "load",
        lambda name, data: data if isinstance(data, dict) else real_load(name, data))
    before = set(tmp_path.rglob("*"))
    res = CliRunner().invoke(app, ["cut", str(video), "--theme", "pessoal", "--dry-run"])
    assert res.exit_code == 0, res.output
    assert "layout: fit (2860x1776)" in res.output
    assert set(tmp_path.rglob("*")) == before


class _FakeProject:
    def __init__(self, video, d, transcript):
        self.video, self.dir, self._t = video, d, transcript

    def require(self, name, _hint):
        return {"clips": [{"id": "clip-01", "start": 0.0, "end": 2.0}]} \
            if name == "clips.json" else self._t


# --- fundo do tema, faixa do conteúdo e zoom no tempo ---
from reel_studio.core.captions import MARGIN_V, H  # noqa: E402
from reel_studio.core.cut import BAND_H, BAND_Y  # noqa: E402

CLIP_INICIO = 140.0
TROCA = 141.35  # troca do clip-02 do zoom_cortes.py


def _regiao(cx, cy):
    return Region(cx - 0.2, cy - 0.15, 0.4, 0.3)


def test_zoom_dinamico_troca_x_e_y_no_tempo():
    steps = ((0.0, _regiao(0.3, 0.3)), (TROCA - CLIP_INICIO, _regiao(0.7, 0.6)))
    lay = Layout("zoom", region=steps[0][1], steps=steps)
    vf = video_filter(lay, TELA, "c.ass")
    assert "if(gte(t\\,1.35)\\," in vf
    crop = vf.split("crop=")[1].split(",pad")[0] if ",pad" in vf else vf
    assert crop.startswith("1144:532:") and crop.count("if(") == 2


def test_zoom_dinamico_sem_troca_usa_valor_fixo():
    lay = Layout("zoom", region=_regiao(0.5, 0.5))
    assert "if(" not in video_filter(lay, TELA, "c.ass")


def test_zoom_dinamico_vem_da_analise(tmp_path, transcript):
    steps = ((0.0, _regiao(0.3, 0.3)), (1.35, _regiao(0.7, 0.6)))
    analise = Analysis(region=steps[0][1], steps=steps)
    clips = {"clips": [{"id": "clip-01", "start": 0.0, "end": 3.2}]}
    jobs = plan(Path("v.mov"), tmp_path, clips, transcript, load_theme("forge"),
                size=TELA, analyzer=lambda *_: analise)
    assert jobs[0].layout.kind == "zoom" and "gte(t" in jobs[0].args[jobs[0].args.index("-vf") + 1]


def test_fundo_usa_a_cor_do_tema():
    forge = load_theme("forge")["colors"]["bg"]
    vf = video_filter(Layout("fit"), TELA, "c.ass", forge)
    assert f"color=0x{forge[1:]}" in vf and "boxblur" not in vf


def test_fundo_invalido_e_rejeitado():
    with pytest.raises(ReelError):
        video_filter(Layout("fit"), TELA, "c.ass", "red;rm")


def test_faixa_termina_acima_da_legenda_lower_third():
    theme = load_theme("forge")
    assert theme["caption"]["position"] == "lower-third"
    topo_legenda = H - MARGIN_V["lower-third"] - theme["caption"]["size"]
    assert BAND_Y + BAND_H <= topo_legenda
    assert f"{BAND_Y}+({BAND_H}-ih)/2" in video_filter(Layout("fit"), TELA, "c.ass")


# --- folga de fala e fade (feat-03-04) ---
from reel_studio.core import cut as cutmod  # noqa: E402
from reel_studio.core.contracts import validate  # noqa: E402
from reel_studio.core.cut import fade_filters, pad_window  # noqa: E402
from reel_studio.core.errors import ContractError  # noqa: E402


def _plan(tmp_path, transcript, start, end, theme=None, analyzer=lambda *_: None):
    clips = {"clips": [{"id": "clip-01", "start": start, "end": end}]}
    return plan(Path("v.mov"), tmp_path, clips, transcript, theme or load_theme("pessoal"),
                size=TELA, analyzer=analyzer)[0]


def test_folga_soma_antes_e_depois():
    assert pad_window(10, 30, 100, 0.40, 0.70) == pytest.approx((9.60, 30.70))


def test_folga_inicio_nao_fica_negativo():
    assert pad_window(0.2, 5, 100, 0.40, 0.70)[0] == 0


def test_folga_fim_limitado_a_duracao():
    assert pad_window(50, 99.8, 100, 0.40, 0.70)[1] == 100


def test_folga_estouro_de_60s_reduz_o_depois_primeiro():
    s, e = pad_window(10, 69.8, 100, 0.40, 0.70)
    assert e - s == pytest.approx(60) and s == pytest.approx(9.80)
    s, e = pad_window(10, 70, 100, 0.40, 0.70)
    assert e - s == pytest.approx(60) and s == pytest.approx(10)


def test_folga_aplicada_no_plan(tmp_path, transcript):
    job = _plan(tmp_path, transcript, 10, 30)
    assert (job.start, job.end) == pytest.approx((9.60, 30.70))
    assert "9.60" in job.args and "21.10" in job.args


def test_fade_no_video_e_no_audio(tmp_path, transcript):
    job = _plan(tmp_path, transcript, 10, 30)
    vf = job.args[job.args.index("-vf") + 1]
    af = job.args[job.args.index("-af") + 1]
    assert "fade=t=in:d=0.25" in vf and "fade=t=out:st=20.65:d=0.45" in vf
    assert "afade=t=in:d=0.25" in af and "afade=t=out:st=20.65:d=0.45" in af


def test_fade_corte_curto_reduz_proporcionalmente():
    vf, _ = fade_filters(0.35, 0.25, 0.45)
    assert "fade=t=in:d=0.12" in vf and "fade=t=out:st=0.12:d=0.23" in vf


def test_fade_zero_nao_gera_filtro():
    assert fade_filters(10, 0, 0) == ("", "")


def test_tema_cut_sobrescreve_os_padroes(tmp_path, transcript):
    theme = {**load_theme("pessoal"), "cut": {"pad_before": 1.0, "pad_after": 0.0, "fade_in": 0}}
    job = _plan(tmp_path, transcript, 10, 30, theme)
    assert (job.start, job.end) == (9.0, 30.0)
    assert "fade=t=in" not in job.args[job.args.index("-vf") + 1]


def test_tema_cut_negativo_e_rejeitado():
    with pytest.raises(ContractError):
        validate("theme", {**load_theme("pessoal"), "cut": {"pad_before": -1}})


def test_folga_zoom_usa_start_com_folga(tmp_path, transcript):
    vistos = []

    def analyzer(_v, start, end):
        vistos.append((start, end))

    _plan(tmp_path, transcript, 10, 30, analyzer=analyzer)
    assert vistos == [pytest.approx((9.60, 30.70))]


# --- preflight do filtro ass ---
FILTROS_COM_ASS = " T.. ass               V->V       Render ASS subtitles.\n"
FILTROS_SEM_ASS = " T.. scale             V->V       Scale the input video.\n"


def _preflight(monkeypatch, filtros, rosetta=False):
    monkeypatch.setattr(cutmod.proc, "capture", lambda _a: filtros)
    monkeypatch.setattr(cutmod.proc, "under_rosetta", lambda: rosetta)


def test_preflight_sem_ass_falha_antes_do_corte(monkeypatch, tmp_path):
    _preflight(monkeypatch, FILTROS_SEM_ASS)
    monkeypatch.setattr(cutmod.proc, "require_bin", lambda *_: "ffmpeg")
    ran = []
    monkeypatch.setattr(cutmod.proc, "run", lambda *a, **k: ran.append(a))
    with pytest.raises(ReelError, match="ffmpeg-full") as e:
        cutmod.execute([], tmp_path)
    assert "arm64" not in str(e.value) and not ran


def test_preflight_com_ass_segue(monkeypatch):
    _preflight(monkeypatch, FILTROS_COM_ASS)
    cutmod.preflight("ffmpeg")


def test_preflight_sob_rosetta_sugere_arm64(monkeypatch):
    _preflight(monkeypatch, FILTROS_SEM_ASS, rosetta=True)
    with pytest.raises(ReelError, match="arch -arm64 brew install ffmpeg-full"):
        cutmod.preflight("ffmpeg")
