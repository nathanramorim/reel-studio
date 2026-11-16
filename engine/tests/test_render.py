import pytest

from reel_studio.core import contracts, contrast, paths, render
from reel_studio.core.captions import build_scene_ass
from reel_studio.core.errors import ReelError

LIGHT = {"id": "claro", "renderer": "remotion", "background": "own",
         "look": {"bg": "#f7f7f4", "palette": ["accent"]}, "scene_types": ["title"]}
GRADIENT = {**LIGHT, "id": "grad",
            "look": {"bg": "linear-gradient(180deg,#141a3c,#3b2a6b)", "palette": ["accent"]}}
BLACK = {**LIGHT, "id": "preto", "look": {"bg": "#000000", "palette": ["accent"]}}
STYLES = [LIGHT, GRADIENT, BLACK, contracts.load_style("isometric-pastel")]


def scene(i, dur=3.0, narration="uma duas tres quatro cinco", source=None):
    s = {"type": "title", "dur": dur, "narration": narration, "text": f"c{i}"}
    return {**s, "source": source} if source else s


def test_captions_cobre_cada_cena_e_respeita_a_duracao():
    theme = contracts.load_theme("forge")
    ass = build_scene_ass([scene(1), scene(2, 2.0)], [3.0, 2.0], theme)
    linhas = [ln for ln in ass.splitlines() if ln.startswith("Dialogue")]
    assert len(linhas) == 4  # 5 palavras = 2 blocos por cena
    assert linhas[1].split(",")[2] == "0:00:03.00"
    assert linhas[-1].split(",")[2] == "0:00:05.00"
    assert "uma duas tres" in linhas[0]


def test_captions_cena_sem_narration_fica_sem_legenda():
    theme = contracts.load_theme("forge")
    ass = build_scene_ass([scene(1, narration=""), scene(2)], [3.0, 3.0], theme)
    linhas = [ln for ln in ass.splitlines() if ln.startswith("Dialogue")]
    assert all(ln.split(",")[1] >= "0:00:03.00" for ln in linhas)


def test_captions_none_nao_gera_legenda(tmp_path, capsys):
    data = {"style": "isometric-pastel", "scenes": [scene(1)]}
    out = render.execute(data, contracts.load_theme("forge"),
                         contracts.load_style("isometric-pastel"), tmp_path, True,
                         tmp_path / "v.mp4", render.Mix("none", "none"))
    assert "legenda=none" in capsys.readouterr().out
    assert not list(tmp_path.glob("*.ass")) and not out.exists()


def test_audio_original_plano_tem_recortes_e_emendas_com_fade():
    cenas = [scene(1, source={"start": 1.0, "end": 4.0}),
             scene(2, source={"start": 5.0, "end": 9.0})]
    filtro = render.audio_filter(cenas, render.durations(cenas, "original"))
    assert "atrim=start=1.000:end=4.000" in filtro and "atrim=start=5.000:end=9.000" in filtro
    assert filtro.count("afade=t=in:d=0.05") == 2
    assert "concat=n=2:v=0:a=1[aout]" in filtro


def test_audio_original_sem_source_lista_as_cenas():
    cenas = [scene(1, source={"start": 0, "end": 2}), scene(2), scene(3)]
    with pytest.raises(ReelError, match="cenas 2, 3"):
        render.check_mix(render.Mix("none", "original"), cenas)


def test_audio_none_nao_gera_fluxo_de_audio():
    cmd = render.mux_args("ffmpeg", paths.Path("s.mp4"), paths.Path("v.mp4"), "a.ass",
                          paths.Path("o.mp4"), [scene(1)], [3.0], render.Mix("narration", "none"))
    assert "-filter_complex" not in cmd and "[aout]" not in cmd and "-c:a" not in cmd


def test_opcao_invalida_e_rejeitada():
    with pytest.raises(ReelError):
        render.check_mix(render.Mix("x", "none"), [scene(1)])
    with pytest.raises(ReelError):
        render.check_mix(render.Mix("none", "x"), [scene(1)])


def test_duracao_com_audio_e_o_maior_entre_dur_e_trecho():
    cenas = [scene(1, dur=3, source={"start": 0, "end": 5}),
             scene(2, dur=6, source={"start": 10, "end": 12}), scene(3, dur=4)]
    assert render.durations(cenas, "original") == [5, 6, 4]
    assert render.durations(cenas, "none") == [3, 6, 4]
    p = render.props({"scenes": cenas}, contracts.load_theme("forge"),
                     contracts.load_style("isometric-pastel"), "original")
    assert [s["dur"] for s in p["scenes"]] == [5, 6, 4]


def _combos():
    for tema in ("forge", "busize", "exemplo"):
        for estilo in STYLES:
            yield tema, estilo


@pytest.mark.parametrize(("tema", "estilo"), list(_combos()),
                         ids=lambda v: v if isinstance(v, str) else v["id"])
def test_contraste_minimo_em_todas_as_combinacoes(tema, estilo):
    ajustado, _ = contrast.resolve(contracts.load_theme(tema), estilo)
    stops = contrast.background_stops(contrast.effective_background(ajustado, estilo))
    c = ajustado["colors"]
    assert contrast.worst_ratio(c["text"], stops) >= 4.5
    assert contrast.worst_ratio(c["muted"], stops) >= 4.5
    assert contrast.worst_ratio(c["accent"], stops) >= 3


def test_contraste_forge_sobre_fundo_claro_traz_texto_escuro():
    forge = contracts.load_theme("forge")
    ajustado, mudou = contrast.resolve(forge, LIGHT)
    assert contrast.luminance(ajustado["colors"]["text"]) < 0.2
    assert {"text", "surface"} <= set(mudou)


def test_contraste_forge_sobre_preto_nao_muda():
    forge = contracts.load_theme("forge")
    ajustado, mudou = contrast.resolve(forge, BLACK)
    assert ajustado == forge and mudou == []


def test_look_ink_vence_o_calculo_automatico():
    forge = contracts.load_theme("forge")
    estilo = {**LIGHT, "look": {**LIGHT["look"], "ink": "#1f2430"}}
    ajustado, _ = contrast.resolve(forge, estilo)
    assert ajustado["colors"]["text"] == "#1f2430"


def test_aviso_so_aparece_quando_houve_ajuste(tmp_path, capsys):
    forge = contracts.load_theme("forge")
    data = {"style": "x", "scenes": [scene(1)]}
    kw = {"workdir": tmp_path, "dry_run": True, "source": tmp_path / "v.mp4",
          "mix": render.Mix("none", "none")}
    render.execute(data, forge, LIGHT, **kw)
    esperado = ("contraste: tema forge sobre estilo claro: "
                "cores ajustadas (text, muted, accent, accent2, surface)")
    assert esperado in capsys.readouterr().out
    render.execute(data, forge, BLACK, **kw)
    assert "contraste" not in capsys.readouterr().out


def test_dry_run_nao_escreve(tmp_path):
    data = {"style": "x", "scenes": [scene(1)]}
    render.execute(data, contracts.load_theme("forge"), contracts.load_style("isometric-pastel"),
                   tmp_path, True, tmp_path / "v.mp4")
    assert list(tmp_path.iterdir()) == []


def test_cores_estilos_entregues_sem_hex_proprio_nem_fundo_own():
    for sid in paths.list_styles():
        st = contracts.load_style(sid)
        assert st["background"] == "theme"
        assert "bg" not in st["look"]
        valores = [*st["look"].get("palette", []), st["look"].get("stroke", ""),
                   st["look"].get("ink", "")]
        assert not any(v.startswith("#") for v in valores)


@pytest.mark.parametrize("sid", paths.list_styles())
def test_cores_props_do_forge_trazem_fundo_e_paleta_do_forge(sid):
    forge = contracts.load_theme("forge")
    p = render.props({"scenes": [scene(1)]}, forge, contracts.load_style(sid))
    assert p["theme"]["colors"] == forge["colors"]
    assert all(c.startswith("#") for c in p["style"]["look"]["palette"])
    if sid == "isometric-pastel":
        assert p["style"]["look"]["palette"][:3] == ["#4f8ef7", "#8aa4ff", "#3ecf8e"]
