"""Requisitos pelo motor vendorizado (scripts/requisitos.py, skills.lock).

Leve: sem rede e sem instalar nada."""

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
TOML = RAIZ / "requisitos.toml"
spec = importlib.util.spec_from_file_location("requisitos", RAIZ / "scripts" / "requisitos.py")
req = importlib.util.module_from_spec(spec)
sys.modules["requisitos"] = req
spec.loader.exec_module(req)


def ambiente(sistema, arch="x64", programas=(), **extra):
    """Máquina falsa: só `programas` existem no PATH; nada roda de verdade."""
    return req.Ambiente(sistema=sistema, arch=arch, home=Path("/casa"), env=extra.pop("env", {}),
                        which=lambda n: f"/bin/{n}" if n in programas else None,
                        executar=lambda argv: (127, ""), rodar=lambda argv: 0,
                        disco_livre_gb=lambda p: 100.0, memoria_gb=lambda: 16.0, **extra)


def itens():
    return {i.id: i for i in req.carregar(str(TOML))[1]}


def test_copia_do_motor_bate_com_o_skills_lock():
    lock = json.loads((RAIZ / "skills.lock").read_text(encoding="utf-8"))["skills"][0]
    assert lock["commit"].startswith("5f63e02")
    for destino, sha in lock["arquivos"].items():
        assert hashlib.sha256((RAIZ / destino).read_bytes()).hexdigest() == sha, destino


def test_receita_valida_nos_tres_sistemas(capsys):
    assert req.main(["--arquivo", str(TOML), "validar"]) == 0
    assert "macos, linux, windows" in capsys.readouterr().out


def test_checar_json_nesta_maquina(capsys):
    codigo = req.main(["--arquivo", str(TOML), "checar", "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert codigo in (0, 1)
    assert {r["id"] for r in dados["requisitos"]} == set(itens())


def test_readme_traz_exatamente_o_prompt_do_motor(capsys):
    assert req.main(["--arquivo", str(TOML), "prompt"]) == 0
    bloco = capsys.readouterr().out.strip()
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert bloco in readme
    assert readme.index(bloco) < readme.index("## Instalação")
    assert "gh repo clone nathanramorim/reel-studio" in bloco


MAQUINAS = [("macos", "arm64"), ("macos", "x64"), ("linux", "x64"), ("linux", "arm64"),
            ("windows", "x64"), ("windows", "arm64")]


@pytest.mark.parametrize("sistema,arch", MAQUINAS)
def test_toda_maquina_sem_gerenciador_tem_receita(sistema, arch):
    """Homebrew, winget e apt nunca são pré-requisito: sem nenhum, todo item diz o que fazer."""
    amb = ambiente(sistema, arch)
    for item in itens().values():
        receita, _ = req.escolher_receita(item, amb)
        assert receita is not None, f"{item.id} sem receita em {sistema} {arch}"


def test_ninguem_aceita_licenca_nem_le_a_chave_pela_pessoa():
    d = itens()
    assert d["licenca-remotion"].tipo == "pessoa" and d["video-e-tema"].tipo == "pessoa"
    assert d["openrouter"].tipo == "credencial"
    assert d["openrouter"].checar == {"env": "OPENROUTER_API_KEY"}
    texto = TOML.read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY" not in "".join(re.findall(r"comandos = (\[\[.*\]\])", texto))


def test_chave_do_openrouter_nunca_aparece_no_checar():
    amb = ambiente("linux", env={"OPENROUTER_API_KEY": "sk-segredo-de-teste"})
    resultados = req.checar(list(itens().values()), amb)
    assert "sk-segredo-de-teste" not in req.em_json(resultados, amb)


def test_python_e_extras_respeitam_o_uv_lock():
    d = itens()
    r, _ = req.escolher_receita(d["python"], ambiente("linux"))
    assert r["comandos"] == [["uv", "python", "install", "3.12"]]
    for extra in ("extra-transcribe", "extra-voice", "extra-vision"):
        r, _ = req.escolher_receita(d[extra], ambiente("linux"))
        cmd = r["comandos"][0]
        assert cmd[:4] == ["uv", "sync", "--project", "{raiz}/engine"]
        assert "3.12" in cmd and "--inexact" in cmd
    r, _ = req.escolher_receita(d["extra-transcribe"], ambiente("macos", "x64"))
    assert "onnxruntime" in r["nao_suportado"]
    for extra in ("extra-transcribe", "extra-voice", "extra-vision", "chrome-headless"):
        r, _ = req.escolher_receita(d[extra], ambiente("windows", "arm64"))
        assert "nao_suportado" in r, extra


def test_ffmpeg_com_libass_no_mac_sem_homebrew_como_unico_caminho():
    d = itens()
    r, _ = req.escolher_receita(d["ffmpeg"], ambiente("macos", "arm64", programas=("brew",)))
    assert r["comandos"][0] == ["brew", "install", "ffmpeg-full"]
    r, _ = req.escolher_receita(d["ffmpeg"], ambiente("macos", "arm64"))
    assert "manual" in r and "brew install" not in r["manual"]
    assert re.search(d["ffmpeg-libass"].checar["regex"],
                     " .. ass               V->V       Render ASS subtitles (libass).")


def test_chrome_baixa_dentro_de_render():
    d = itens()
    r, _ = req.escolher_receita(d["chrome-headless"], ambiente("linux"))
    assert r["comandos"] == [["npm", "--prefix", "{raiz}/render", "run", "browser"]]
    pacote = json.loads((RAIZ / "render" / "package.json").read_text(encoding="utf-8"))
    assert pacote["scripts"]["browser"] == "remotion browser ensure"
