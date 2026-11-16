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


def test_padrao_voz_original_quando_todas_as_cenas_tem_source():
    src = {"start": 0, "end": 2}
    assert render.default_audio([{"source": src}, {"source": src}]) == "original"


def test_padrao_voz_none_sem_source_ou_parcial_ou_vazio():
    src = {"start": 0, "end": 2}
    assert render.default_audio([{"source": src}, {}]) == "none"
    assert render.default_audio([{}]) == "none"
    assert render.default_audio([]) == "none"


# --- estilo forge-motion (05-05) ---
def test_forge_motion_valida_e_resolve_paleta_pelo_tema():
    from reel_studio.core.contracts import load_style, load_theme
    from reel_studio.core.render import props

    style, theme = load_style("forge-motion"), load_theme("forge")
    assert style["look"]["motion"] == "forge" and style["background"] == "theme"
    out = props({"scenes": [{"type": "flow", "dur": 4, "narration": "x", "steps": ["a", "b"]}]},
                theme, style)
    colors = theme["colors"]
    assert out["style"]["look"]["palette"] == [colors["accent"], colors["accent2"],
                                               colors["success"]]


def test_forge_motion_aceita_tema_sem_brand():
    from reel_studio.core.contracts import load_style, load_theme
    from reel_studio.core.render import props

    theme = load_theme("exemplo")
    assert "brand" not in theme
    out = props({"scenes": [{"type": "cta", "dur": 3, "narration": "x"}]}, theme,
                load_style("forge-motion"))
    assert out["style"]["id"] == "forge-motion"


# --- 05-06 a 05-12 ---
TRANSCRICAO = {"segments": [{"start": 0, "end": 4, "text": "a b c", "words": [
    {"start": 5.0, "end": 5.4, "word": "um"}, {"start": 5.5, "end": 6.0, "word": "dois"},
    {"start": 9.0, "end": 9.5, "word": "fora"}]}]}


def test_palavras_remapeadas_pelo_source():
    cena = scene(1, source={"start": 4.0, "end": 7.0})
    palavras = render.scene_words(cena, 3.0, "original", TRANSCRICAO)
    assert [w["word"] for w in palavras] == ["um", "dois"]
    assert palavras[0]["start"] == pytest.approx(1.0)
    assert all(0 <= w["start"] <= w["end"] <= 3.0 for w in palavras)


def test_palavras_fallback_uniforme_nunca_antes_da_cena():
    palavras = render.scene_words(scene(1, narration="a b c d"), 4.0, "none", None)
    assert [w["start"] for w in palavras] == [0.0, 1.0, 2.0, 3.0]
    assert palavras[-1]["end"] == 4.0


def test_palavras_voz_gerada_usa_os_tempos_do_audio():
    gerado = [{"word": "oi", "start": -0.2, "end": 9.0}]
    palavras = render.scene_words(scene(1), 3.0, "none", None, gerado)
    assert palavras == [{"word": "oi", "start": 0.0, "end": 3.0}]


def test_props_entrega_words_e_transicao_do_tom():
    dados = {"style": "forge-motion", "tone": "chaotic",
             "scenes": [scene(1), {**scene(2), "transition": "cut"}]}
    out = render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"))
    assert [s["transition"] for s in out["scenes"]] == ["wipe", "cut"]
    assert out["scenes"][0]["words"]


def test_transicao_padrao_sem_tom_e_dip():
    dados = {"style": "forge-motion", "scenes": [scene(1)]}
    out = render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"))
    assert out["scenes"][0]["transition"] == "dip"


def test_transicao_invalida_no_schema():
    with pytest.raises(Exception, match="transition|wipe|fade"):
        contracts.validate("scenes", {"style": "x", "scenes": [{**scene(1), "transition": "fade"}]})


def test_media_plano_referencia_o_video_pelo_public_dir(tmp_path, capsys):
    dados = {"style": "forge-motion", "scenes": [
        {**scene(1), "media": {"source": {"start": 2, "end": 6}}}]}
    video = tmp_path / "v.mp4"
    out = render.execute(dados, contracts.load_theme("forge"),
                         contracts.load_style("forge-motion"), tmp_path, True, video,
                         render.Mix("none", "none", "off"))
    texto = capsys.readouterr().out
    assert f"--public-dir={tmp_path / render.PUBLIC_DIR}" in texto
    assert "aviso:" in texto and "dados sensíveis" in texto
    assert not (tmp_path / render.PUBLIC_DIR).exists() and not out.exists()


def test_media_props_tem_recorte_e_arquivo(tmp_path):
    from reel_studio.core.frames import Analysis, Region
    dados = {"style": "forge-motion", "scenes": [
        {**scene(1), "media": {"source": {"start": 2, "end": 6}}}]}
    video = tmp_path / "v.mp4"
    out = render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"),
                       video=video, analyzer=lambda *_: Analysis(region=Region(0.1, 0.2, 0.5, 0.4)))
    m = out["scenes"][0]["media"]
    assert m["file"] == "v.mp4" and m["region"]["w"] == 0.5 and (m["start"], m["end"]) == (2, 6)


def test_cena_sem_media_nao_muda():
    dados = {"style": "forge-motion", "scenes": [scene(1)]}
    out = render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"))
    assert "media" not in out["scenes"][0]
    assert render.args("npx", paths.Path("p.json"), paths.Path("o.mp4")) == [
        "npx", "remotion", "render", "src/index.ts", "Reel", "o.mp4", "--props=p.json",
        "--codec=h264"]


def test_media_sem_video_levanta_erro():
    dados = {"style": "forge-motion", "scenes": [
        {**scene(1), "media": {"source": {"start": 0, "end": 1}}}]}
    with pytest.raises(ReelError, match="media"):
        render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"))


def _dry(tmp_path, capsys, mix, dados=None):
    dados = dados or {"style": "forge-motion", "scenes": [scene(1), scene(2)]}
    render.execute(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"),
                   tmp_path, True, None, mix)
    return capsys.readouterr().out


def test_musica_auto_liga_sem_voz_e_desliga_com_voz(tmp_path, capsys):
    assert "trilha" in _dry(tmp_path, capsys, render.Mix("none", "none", "auto"))
    com_voz = {"style": "forge-motion", "scenes": [scene(1, source={"start": 0, "end": 3})]}
    cmd = render.Mix("none", "original", "auto")
    render.execute(com_voz, contracts.load_theme("forge"), contracts.load_style("forge-motion"),
                   tmp_path, True, tmp_path / "v.mp4", cmd)
    assert "trilha" not in capsys.readouterr().out
    assert "trilha" not in _dry(tmp_path, capsys, render.Mix("none", "none", "off"))


def test_ducking_so_com_voz_e_trilha():
    cenas = [scene(1, source={"start": 0, "end": 3})]
    mix = render.Mix("none", "original", "on")
    cmd = render.mux_args("ffmpeg", paths.Path("s.mp4"), paths.Path("v.mp4"), "a.ass",
                          paths.Path("o.mp4"), cenas, [3.0], mix, paths.Path("m.wav"))
    filtro = cmd[cmd.index("-filter_complex") + 1]
    assert "sidechaincompress" in filtro and "[1:a]atrim" in filtro and "-shortest" in cmd
    sem_voz = render.mux_args("ffmpeg", paths.Path("s.mp4"), None, "a.ass", paths.Path("o.mp4"),
                              cenas, [3.0], render.Mix("none", "none", "on"), paths.Path("m.wav"))
    assert "sidechaincompress" not in " ".join(sem_voz) and "[mix]" in sem_voz


def test_musica_encaixa_cortes_na_batida():
    cenas = [scene(1, dur=3.1), scene(2, dur=3.0)]
    durs = render.durations(cenas, "none", bpm=120)
    assert durs[0] == pytest.approx(3.0)


def test_voz_gerada_define_duracao_e_palavras(tmp_path):
    from reel_studio.core.voice import Voice
    v = Voice([], [4.2], [[{"word": "oi", "start": 0.1, "end": 0.4}]], tmp_path / "j.wav")
    dados = {"style": "forge-motion", "scenes": [scene(1, dur=3.0)]}
    out = render.props(dados, contracts.load_theme("forge"), contracts.load_style("forge-motion"),
                       voice=v)
    assert out["scenes"][0]["dur"] == 4.2 and out["scenes"][0]["words"][0]["word"] == "oi"


def test_poster_troca_o_quadro_0_sem_mudar_a_duracao():
    from reel_studio.core import deliver
    cmd = deliver.replace_first_args("ffmpeg", paths.Path("v.mp4"), paths.Path("p.jpg"),
                                     paths.Path("o.mp4"))
    assert "overlay=enable='eq(n,0)'" in " ".join(cmd)
    assert "-t" not in cmd and "-shortest" not in cmd and "copy" in cmd
    assert deliver.poster_time(3.0) == pytest.approx(2.0)
    assert deliver.poster_time(1.0) == pytest.approx(0.9)


def test_share_sai_do_campo_share_e_sem_share_nao_gera(tmp_path):
    from reel_studio.core import deliver
    arq = deliver.write_share("Um. Dois! Três? Quatro.", tmp_path)
    assert arq.read_text() == "Um. Dois! Três?\n"
    assert deliver.write_share(None, tmp_path) is None
    assert deliver.write_share("  ", tmp_path) is None


def test_dry_run_anuncia_poster_e_share(tmp_path, capsys):
    dados = {"style": "forge-motion", "share": "Texto.", "scenes": [scene(1)]}
    texto = _dry(tmp_path, capsys, render.Mix("none", "none", "off"), dados)
    assert "pôster" in texto and "share-copy.txt" in texto
    assert not list(tmp_path.iterdir())
