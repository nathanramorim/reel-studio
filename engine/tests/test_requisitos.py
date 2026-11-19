"""scripts/requisitos.py: checar e instalar sem tocar a máquina (tudo injetado)."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "requisitos.py"
_spec = importlib.util.spec_from_file_location("requisitos", SCRIPT)
req = importlib.util.module_from_spec(_spec)
sys.modules["requisitos"] = req
_spec.loader.exec_module(req)

TODOS = {"uv", "ffmpeg", "ffprobe", "node", "sysctl", "brew"}
FILTROS_COM_ASS = " ... ass               V->V       Render ASS subtitles (libass)."


def raiz_falsa(tmp_path: Path, npm: bool = True) -> Path:
    (tmp_path / "engine").mkdir()
    (tmp_path / "engine" / "pyproject.toml").write_text("[project]\n")
    render = tmp_path / "render"
    render.mkdir()
    (render / "package.json").write_text("{}")
    (render / "package-lock.json").write_text(json.dumps(
        {"packages": {"node_modules/remotion": {"version": "4.0.543"}}}))
    if npm:
        (render / "node_modules" / "remotion").mkdir(parents=True)
        (render / "node_modules" / ".remotion" / "chrome-headless-shell").mkdir(parents=True)
    return tmp_path


def home_com_modelos(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    snap = home / ".cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/x"
    snap.mkdir(parents=True)
    (snap / "model.bin").write_bytes(b"0")
    ckpt = home / ".cache/torch/hub/checkpoints"
    ckpt.mkdir(parents=True)
    (ckpt / "htdemucs.th").write_bytes(b"0")
    return home


def ambiente(tmp_path, programas=TODOS, filtros=FILTROS_COM_ASS, extras_ok=True,
             rosetta=False, raiz=True, env=None, chamadas=None):
    chamadas = [] if chamadas is None else chamadas

    def executar(args, cwd=None):
        chamadas.append((args, cwd))
        if args[:2] == ["uv", "--version"]:
            return 0, "uv 0.9.7 (abc)"
        if args[:3] == ["uv", "python", "find"]:
            return 0, "/py/bin/python3"
        if args == ["/py/bin/python3", "--version"]:
            return 0, "Python 3.11.9"
        if args[:2] == ["ffmpeg", "-version"]:
            return 0, "ffmpeg version 8.0.1 Copyright"
        if args[:2] == ["ffmpeg", "-hide_banner"]:
            return 0, filtros
        if args[:3] == ["uv", "run", "--no-sync"]:
            return (0 if extras_ok else 1), ""
        if args == ["node", "--version"]:
            return 0, "v22.3.0"
        if args[0] == "sysctl":
            return 0, "1" if rosetta else "0"
        return 0, ""

    return req.Ambiente(
        raiz=raiz_falsa(tmp_path) if raiz else None,
        home=home_com_modelos(tmp_path),
        env=env or {},
        sistema="Darwin",
        executar=executar,
        which=lambda nome: f"/bin/{nome}" if nome in programas else None,
    )


def por_nome(reqs):
    return {r.nome: r for r in reqs}


def test_tudo_ok_sem_obrigatorio_faltando(tmp_path):
    reqs = req.checar(ambiente(tmp_path))
    r = por_nome(reqs)
    assert not req.falta_obrigatorio(reqs)
    assert r["uv"].versao == "0.9.7"
    assert r["python"].versao == "3.11.9"
    assert r["ffmpeg-libass"].estado == req.OK
    assert r["render-npm"].versao == "remotion 4.0.543"
    assert all(x.estado == req.OK for x in reqs if x.tipo != req.SEU)


def test_ffmpeg_ausente_e_obrigatorio_com_brew(tmp_path):
    r = por_nome(req.checar(ambiente(tmp_path, programas=TODOS - {"ffmpeg"})))
    assert r["ffmpeg"].estado == req.FALTANDO and r["ffmpeg"].obrigatorio
    assert r["ffmpeg"].comandos == [["brew", "install", "ffmpeg-full"]]


def test_ffmpeg_sem_libass_pede_ffmpeg_full_e_link(tmp_path):
    r = por_nome(req.checar(ambiente(tmp_path, filtros=" ... subtitles  V->V")))
    assert r["ffmpeg-libass"].estado == req.FALTANDO
    assert r["ffmpeg-libass"].comandos == [
        ["brew", "install", "ffmpeg-full"],
        ["brew", "link", "--overwrite", "--force", "ffmpeg-full"],
    ]


def test_rosetta_poe_arch_arm64(tmp_path):
    r = por_nome(req.checar(ambiente(tmp_path, programas=TODOS - {"uv"}, rosetta=True)))
    assert r["uv"].comandos == [["arch", "-arm64", "brew", "install", "uv"]]


def test_extras_faltando_usam_sync_inexato_na_pasta_engine(tmp_path):
    amb = ambiente(tmp_path, extras_ok=False)
    r = por_nome(req.checar(amb))
    assert r["extra-transcribe"].estado == req.FALTANDO and r["extra-transcribe"].obrigatorio
    assert r["extra-voice"].estado == req.OPCIONAL and not r["extra-voice"].obrigatorio
    assert r["extra-transcribe"].comandos == [["uv", "sync", "--inexact", "--extra", "transcribe"]]
    assert r["extra-transcribe"].pasta == str(amb.raiz / "engine")


def test_sem_raiz_itens_do_projeto_ficam_para_depois_sem_comando(tmp_path):
    reqs = req.checar(ambiente(tmp_path, raiz=False, extras_ok=False))
    r = por_nome(reqs)
    for nome in ("extra-transcribe", "render-npm", "chrome-headless"):
        assert r[nome].comandos == []
        assert "depois de instalar o plugin" in r[nome].explicacao
    assert req.falta_obrigatorio(reqs)


def test_whisper_respeita_reel_whisper_model(tmp_path):
    r = por_nome(req.checar(ambiente(tmp_path, env={"REEL_WHISPER_MODEL": "medium"})))
    assert r["whisper-medium"].estado == req.OPCIONAL
    assert "WhisperModel('medium')" in r["whisper-medium"].comandos[0][-1]


def test_whisper_com_valor_invalido_fica_faltando_e_avisa(tmp_path):
    reqs = req.checar(ambiente(tmp_path, env={"REEL_WHISPER_MODEL": "x'; rm"}))
    r = por_nome(reqs)["whisper-modelo"]
    assert r.estado == req.FALTANDO and r.obrigatorio and r.tipo == req.SEU
    assert r.comandos == []
    assert "o motor recusa" in r.explicacao and "large-v3" in r.explicacao
    assert "x'; rm" not in req.em_tabela(reqs)
    assert req.falta_obrigatorio(reqs)


def test_openrouter_nunca_le_a_chave(tmp_path):
    amb = ambiente(tmp_path, env={"OPENROUTER_API_KEY": "sk-segredo"})
    saida = req.em_json(req.checar(amb)) + req.em_tabela(req.checar(amb))
    assert "sk-segredo" not in saida
    assert por_nome(req.checar(amb))["openrouter"].tipo == req.SEU


def test_json_tem_ok_e_requisitos(tmp_path):
    dados = json.loads(req.em_json(req.checar(ambiente(tmp_path, programas=TODOS - {"uv"}))))
    assert dados["ok"] is False
    campos = {"nome", "estado", "versao", "obrigatorio", "tipo", "explicacao", "comandos"}
    assert campos <= set(dados["requisitos"][0])


def test_tabela_tem_colunas_e_rodape(tmp_path):
    texto = req.em_tabela(req.checar(ambiente(tmp_path)))
    assert texto.startswith("| Requisito | Estado | Versão | Como resolver |")
    assert "Todos os obrigatórios estão ok." in texto


def _instalar(amb, **kw):
    rodados, linhas = [], []
    codigo = req.instalar(amb, saida=linhas.append,
                          executor=lambda c, cwd=None: rodados.append((c, cwd)) or (0, ""), **kw)
    return codigo, rodados, "\n".join(linhas)


def test_instalar_nada_pendente_nao_roda_nada(tmp_path):
    amb = ambiente(tmp_path)
    # só os itens "seu" ficam pendentes e eles nunca rodam
    codigo, rodados, texto = _instalar(amb, sim=True, interativo=False)
    assert codigo == 0 and rodados == []
    assert "Este item é seu" in texto


def test_instalar_sim_roda_so_o_que_falta_e_nunca_itens_seus(tmp_path):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"})
    codigo, rodados, _ = _instalar(amb, sim=True, interativo=False)
    comandos = [c for c, _ in rodados]
    assert ["brew", "install", "ffmpeg-full"] in comandos
    assert not any("remotion.dev" in " ".join(c) or "OPENROUTER" in " ".join(c) for c in comandos)
    assert codigo == 0


def test_instalar_sem_terminal_e_sem_sim_so_mostra(tmp_path):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"})
    codigo, rodados, texto = _instalar(amb, sim=False, interativo=False)
    assert rodados == [] and codigo == 0
    assert "brew install ffmpeg-full" in texto
    assert "Nada foi rodado" in texto
    assert "`instalar --sim <item>`" in texto and "ok da pessoa" in texto
    assert "Itens que dá para instalar: ffmpeg, ffmpeg-libass." in texto
    assert "todos" not in texto


def test_instalar_sem_terminal_com_item_nunca_sugere_todos(tmp_path):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"}, extras_ok=False)
    codigo, rodados, texto = _instalar(amb, sim=False, interativo=False, itens=["extra-voice"])
    assert rodados == [] and codigo == 1  # o item pedido continua faltando
    assert "todos" not in texto
    assert "Itens que dá para instalar: extra-voice." in texto


@pytest.mark.parametrize(("resposta", "roda"), [("s", True), ("n", False), ("", False)])
def test_instalar_pergunta_antes_de_cada_item(tmp_path, resposta, roda):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"})
    perguntas = []
    codigo, rodados, _ = _instalar(
        amb, sim=False, interativo=True, perguntar=lambda p: perguntas.append(p) or resposta)
    assert perguntas and all("Rodar agora? [s/N]" in p for p in perguntas)
    assert bool(rodados) is roda


def test_instalar_falha_devolve_codigo_1(tmp_path):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"})
    linhas = []
    codigo = req.instalar(amb, sim=True, interativo=False, saida=linhas.append,
                          executor=lambda c, cwd=None: (1, "erro do brew"))
    assert codigo == 1
    assert any("Falhou (código 1): erro do brew" in x for x in linhas)


def test_main_checar_sai_1_quando_falta(monkeypatch, tmp_path, capsys):
    amb = ambiente(tmp_path, programas=TODOS - {"uv"})
    monkeypatch.setattr(req, "Ambiente", lambda raiz: amb)
    assert req.main(["checar", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_acha_o_plugin_instalado_mais_novo(monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(req, "__file__", str(tmp_path / "solto" / "requisitos.py"))
    cache = tmp_path / "home/.claude/plugins/cache/reel-studio/reel-studio"
    for v in ("0.1.0", "0.10.0", "0.2.0"):
        raiz_falsa_em(cache / v)
    assert req.achar_raiz(None, home=tmp_path / "home") == cache / "0.10.0"


def test_sem_plugin_nem_clone_nao_acha_raiz(monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(req, "__file__", str(tmp_path / "solto" / "requisitos.py"))
    assert req.achar_raiz(None, home=tmp_path / "home") is None


def raiz_falsa_em(pasta: Path) -> None:
    (pasta / "engine").mkdir(parents=True)
    (pasta / "engine" / "pyproject.toml").write_text("[project]\n")
    (pasta / "render").mkdir()
    (pasta / "render" / "package.json").write_text("{}")


def test_instalar_com_item_cuida_so_dele(tmp_path):
    amb = ambiente(tmp_path, programas=TODOS - {"ffmpeg"}, extras_ok=False)
    codigo, rodados, texto = _instalar(amb, sim=True, interativo=False, itens=["extra-voice"])
    assert codigo == 1  # no ambiente falso o extra segue ausente depois do comando
    assert [c for c, _ in rodados] == [["uv", "sync", "--inexact", "--extra", "voice"]]
    assert "ffmpeg" not in texto


def test_instalar_item_ja_ok_nao_roda_nada(tmp_path):
    codigo, rodados, texto = _instalar(ambiente(tmp_path), sim=True, interativo=False,
                                       itens=["ffmpeg"])
    assert codigo == 0 and rodados == []
    assert "Nada a instalar" in texto


def test_instalar_item_desconhecido_sai_2_com_a_lista(tmp_path):
    codigo, rodados, texto = _instalar(ambiente(tmp_path), sim=True, interativo=False,
                                       itens=["ffmpeg", "nao-existe"])
    assert codigo == 2 and rodados == []
    assert "nao-existe" in texto and "Itens válidos:" in texto and "extra-transcribe" in texto


def test_main_instalar_repassa_os_itens(monkeypatch, tmp_path):
    amb = ambiente(tmp_path)
    monkeypatch.setattr(req, "Ambiente", lambda raiz: amb)
    assert req.main(["instalar", "--sim", "nao-existe"]) == 2


def test_instalar_item_pedido_que_continua_faltando_sai_1(tmp_path):
    # o comando "roda" (executor falso devolve 0), mas o extra continua ausente na rechecagem
    amb = ambiente(tmp_path, extras_ok=False)
    codigo, rodados, texto = _instalar(amb, sim=True, interativo=False, itens=["extra-voice"])
    assert rodados and codigo == 1
    assert "Ainda não está ok: extra-voice." in texto


def test_instalar_item_seu_pedido_nao_conta_como_falha(tmp_path):
    codigo, rodados, _ = _instalar(ambiente(tmp_path), sim=True, interativo=False,
                                   itens=["openrouter"])
    assert codigo == 0 and rodados == []
