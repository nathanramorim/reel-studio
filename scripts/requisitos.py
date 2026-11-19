#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Confere e instala os requisitos do reel-studio.

Uso:
  uv run scripts/requisitos.py checar [--json] [--raiz PASTA]
  uv run scripts/requisitos.py instalar [--sim] [--raiz PASTA]

Roda antes de clonar (pela URL do arquivo) e antes dos extras: só usa a biblioteca padrão.
`checar` mostra cada requisito (ok, faltando ou opcional) e sai com código 1 se faltar um
obrigatório. `instalar` mostra o comando de cada item que falta e pergunta antes de rodar;
com `--sim`, roda sem perguntar. Nunca aceita licença nem declaração por você e nunca lê
chaves: esses itens só são explicados.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

OK, FALTANDO, OPCIONAL = "ok", "faltando", "opcional"
SISTEMA, PROJETO, DOWNLOAD, SEU = "sistema", "projeto", "download", "seu"
NODE_MINIMO = 18
WHISPER_MODELOS = ("tiny", "base", "small", "medium", "large-v3")
REPO = "https://github.com/nathanramorim/reel-studio"


@dataclass
class Requisito:
    nome: str
    estado: str
    versao: str
    obrigatorio: bool
    tipo: str
    explicacao: str
    comandos: list[list[str]] = field(default_factory=list)
    pasta: str = ""  # onde rodar os comandos ("" = pasta atual)


def executar(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    """Roda sem shell e devolve (código, stdout+stderr); (127, '') se o programa não existe."""
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=120,
                           check=False)
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return r.returncode, (r.stdout + r.stderr).strip()


@dataclass
class Ambiente:
    """Tudo o que a checagem consulta; injetável para testar sem tocar a máquina."""

    raiz: Path | None
    home: Path = field(default_factory=Path.home)
    env: dict = field(default_factory=lambda: dict(os.environ))
    sistema: str = field(default_factory=platform.system)
    executar: Callable[[list[str], str | None], tuple[int, str]] = executar
    which: Callable[[str], str | None] = shutil.which

    def rodar(self, args: list[str], cwd: Path | None = None) -> tuple[int, str]:
        return self.executar(args, str(cwd) if cwd else None)


def _versao_chave(pasta: Path) -> tuple:
    return tuple(int(n) if n.isdigit() else 0 for n in re.split(r"[.-]", pasta.name))


def achar_raiz(explicita: str | None, home: Path | None = None) -> Path | None:
    """Pasta do reel-studio: --raiz, CLAUDE_PLUGIN_ROOT, a pasta deste script, a atual (ou
    acima) ou o plugin instalado no Claude Code (a versão mais nova)."""
    atual = Path.cwd()
    candidatos = [explicita, os.environ.get("CLAUDE_PLUGIN_ROOT"),
                  str(Path(__file__).resolve().parent.parent),
                  *(str(p) for p in (atual, *atual.parents))]
    cache = (home or Path.home()) / ".claude/plugins/cache/reel-studio/reel-studio"
    if cache.is_dir():
        versoes = sorted((p for p in cache.iterdir() if p.is_dir()), key=_versao_chave)
        candidatos += [str(p) for p in reversed(versoes)]
    for c in candidatos:
        if c and (Path(c) / "engine" / "pyproject.toml").is_file() \
                and (Path(c) / "render" / "package.json").is_file():
            return Path(c)
    return None


def _primeira_linha(texto: str) -> str:
    return texto.splitlines()[0] if texto else ""


def sob_rosetta(amb: Ambiente) -> bool:
    """Mesmo critério do motor (core/proc.under_rosetta), copiado para ficar só com stdlib."""
    if amb.sistema != "Darwin" or not amb.which("sysctl"):
        return False
    codigo, saida = amb.rodar(["sysctl", "-n", "sysctl.proc_translated"])
    return codigo == 0 and saida.strip() == "1"


def _brew(amb: Ambiente, *formula: str) -> list[list[str]]:
    if amb.sistema != "Darwin":
        return []
    cmd = ["brew", "install", *formula]
    return [["arch", "-arm64", *cmd] if sob_rosetta(amb) else cmd]


# ---------- checagens ----------

def check_uv(amb: Ambiente) -> Requisito:
    explic = "Gerencia o Python e as dependências do motor (nunca use pip)."
    if not amb.which("uv"):
        if amb.sistema != "Darwin":
            explic += " Instale pelo site: https://docs.astral.sh/uv/"
        return Requisito("uv", FALTANDO, "", True, SISTEMA, explic, _brew(amb, "uv"))
    _, saida = amb.rodar(["uv", "--version"])
    m = re.search(r"uv (\S+)", saida)
    return Requisito("uv", OK, m.group(1) if m else "", True, SISTEMA, explic)


def check_python(amb: Ambiente) -> Requisito:
    explic = "O motor precisa do Python 3.11 ou mais novo; o uv instala, você não instala à mão."
    cmd = [["uv", "python", "install", "3.11"]]
    if not amb.which("uv"):
        return Requisito("python", FALTANDO, "", True, PROJETO, explic + " Instale o uv antes.",
                         cmd)
    codigo, saida = amb.rodar(["uv", "python", "find", ">=3.11"])
    if codigo != 0 or not saida:
        return Requisito("python", FALTANDO, "", True, PROJETO, explic, cmd)
    _, versao = amb.rodar([_primeira_linha(saida), "--version"])
    m = re.search(r"Python (\S+)", versao)
    return Requisito("python", OK, m.group(1) if m else "3.11+", True, PROJETO, explic)


def check_ffmpeg(amb: Ambiente) -> Requisito:
    explic = "Corta o vídeo, extrai o áudio e mede as dimensões (ffmpeg e ffprobe)."
    cmd = _brew(amb, "ffmpeg-full")
    if amb.sistema == "Windows":
        cmd = [["winget", "install", "ffmpeg"]]
    if not amb.which("ffmpeg") or not amb.which("ffprobe"):
        return Requisito("ffmpeg", FALTANDO, "", True, SISTEMA, explic, cmd)
    _, saida = amb.rodar(["ffmpeg", "-version"])
    m = re.match(r"ffmpeg version (\S+)", saida)
    return Requisito("ffmpeg", OK, m.group(1) if m else "", True, SISTEMA, explic)


def check_libass(amb: Ambiente) -> Requisito:
    """Mesmo critério do preflight do corte (core/cut.preflight): o filtro `ass` existe."""
    explic = ("A legenda do tema usa o filtro 'ass' do ffmpeg (libass). No Mac, o ffmpeg-full "
              "tem; ele é keg-only, então o brew link põe ele no PATH no lugar do ffmpeg comum.")
    cmd = _brew(amb, "ffmpeg-full")
    if amb.sistema == "Darwin":
        link = ["brew", "link", "--overwrite", "--force", "ffmpeg-full"]
        cmd.append(["arch", "-arm64", *link] if sob_rosetta(amb) else link)
    elif amb.sistema == "Windows":
        cmd = [["winget", "install", "ffmpeg"]]
    if not amb.which("ffmpeg"):
        return Requisito("ffmpeg-libass", FALTANDO, "", True, SISTEMA, explic, cmd)
    _, saida = amb.rodar(["ffmpeg", "-hide_banner", "-filters"])
    tem = any(len(p := linha.split()) >= 2 and p[1] == "ass" for linha in saida.splitlines())
    if not tem:
        return Requisito("ffmpeg-libass", FALTANDO, "", True, SISTEMA, explic, cmd)
    return Requisito("ffmpeg-libass", OK, "filtro ass", True, SISTEMA, explic)


SEM_RAIZ = ("Fica para depois de instalar o plugin (ou clonar): rode o `instalar` de novo; "
            "ele acha o plugin sozinho (ou passe --raiz PASTA).")


def _extra(amb: Ambiente, nome: str, modulo: str, obrig: bool, explic: str) -> Requisito:
    estado_falta = FALTANDO if obrig else OPCIONAL
    rotulo = f"extra-{nome}"
    if amb.raiz is None:
        return Requisito(rotulo, estado_falta, "", obrig, PROJETO, f"{explic} {SEM_RAIZ}")
    engine = amb.raiz / "engine"
    cmd = [["uv", "sync", "--inexact", "--extra", nome]]
    if not amb.which("uv"):
        return Requisito(rotulo, estado_falta, "", obrig, PROJETO, explic, cmd, str(engine))
    teste = ("import importlib.util,sys;"
             f"sys.exit(0 if importlib.util.find_spec('{modulo}') else 1)")
    codigo, _ = amb.rodar(["uv", "run", "--no-sync", "python", "-c", teste], engine)
    if codigo != 0:
        return Requisito(rotulo, estado_falta, "", obrig, PROJETO, explic, cmd, str(engine))
    return Requisito(rotulo, OK, "instalado", obrig, PROJETO, explic, pasta=str(engine))


def check_extra_transcribe(amb: Ambiente) -> Requisito:
    return _extra(amb, "transcribe", "faster_whisper", True,
                  "Transcrição local com faster-whisper (os dois modos precisam).")


def check_extra_voice(amb: Ambiente) -> Requisito:
    return _extra(amb, "voice", "demucs", False,
                  "Só para isolar a voz do fundo (`extract --voice-only`); traz o demucs e o "
                  "PyTorch (perto de 1 GB).")


def check_extra_vision(amb: Ambiente) -> Requisito:
    return _extra(amb, "vision", "cv2", False,
                  "Só para o enquadramento automático no corte (acha rosto e área com "
                  "movimento); usa o OpenCV.")


def _hf_cache(amb: Ambiente) -> Path:
    if amb.env.get("HF_HUB_CACHE"):
        return Path(amb.env["HF_HUB_CACHE"])
    base = Path(amb.env["HF_HOME"]) if amb.env.get("HF_HOME") else amb.home / ".cache/huggingface"
    return base / "hub"


def check_whisper_modelo(amb: Ambiente) -> Requisito:
    modelo = amb.env.get("REEL_WHISPER_MODEL") or "small"
    if modelo not in WHISPER_MODELOS:
        modelo = "small"
    nome = f"whisper-{modelo}"
    explic = (f"Modelo do Whisper (REEL_WHISPER_MODEL, padrão small, cerca de 480 MB) em "
              f"{_hf_cache(amb)}. Baixa sozinho na primeira transcrição; adiantar evita a espera.")
    pasta = _hf_cache(amb) / f"models--Systran--faster-whisper-{modelo}" / "snapshots"
    if any(p.is_file() for p in pasta.glob("*/model.bin")):
        return Requisito(nome, OK, "baixado", False, DOWNLOAD, explic)
    if amb.raiz is None:
        return Requisito(nome, OPCIONAL, "", False, DOWNLOAD, f"{explic} {SEM_RAIZ}")
    baixar = f"from faster_whisper import WhisperModel; WhisperModel('{modelo}')"
    cmd = [["uv", "run", "--no-sync", "python", "-c", baixar]]
    return Requisito(nome, OPCIONAL, "", False, DOWNLOAD,
                     explic + " Precisa do extra-transcribe antes.", cmd,
                     str(amb.raiz / "engine"))


def check_demucs_modelo(amb: Ambiente) -> Requisito:
    base = Path(amb.env["TORCH_HOME"]) if amb.env.get("TORCH_HOME") else amb.home / ".cache/torch"
    pasta = base / "hub" / "checkpoints"
    explic = (f"Modelo htdemucs do demucs (cerca de 80 MB) em {pasta}. Só para isolar a voz; "
              "baixa sozinho no primeiro uso.")
    if any(p.is_file() for p in pasta.glob("*.th")):
        return Requisito("demucs-modelo", OK, "baixado", False, DOWNLOAD, explic)
    if amb.raiz is None:
        return Requisito("demucs-modelo", OPCIONAL, "", False, DOWNLOAD, f"{explic} {SEM_RAIZ}")
    baixar = "from demucs.pretrained import get_model; get_model('htdemucs')"
    cmd = [["uv", "run", "--no-sync", "python", "-c", baixar]]
    return Requisito("demucs-modelo", OPCIONAL, "", False, DOWNLOAD,
                     explic + " Precisa do extra-voice antes.", cmd, str(amb.raiz / "engine"))


def check_node(amb: Ambiente) -> Requisito:
    explic = (f"Node.js {NODE_MINIMO} ou mais novo: só para o modo VSL e os componentes do "
              "corte (Remotion).")
    cmd = _brew(amb, "node")
    if amb.sistema == "Windows":
        cmd = [["winget", "install", "OpenJS.NodeJS.LTS"]]
    if not amb.which("node"):
        return Requisito("node", OPCIONAL, "", False, SISTEMA, explic, cmd)
    _, saida = amb.rodar(["node", "--version"])
    m = re.match(r"v(\d+)\.", saida)
    if not m or int(m.group(1)) < NODE_MINIMO:
        return Requisito("node", OPCIONAL, saida, False, SISTEMA,
                         f"{explic} A versão instalada é antiga.", cmd)
    return Requisito("node", OK, saida, False, SISTEMA, explic)


def _versao_remotion(raiz: Path) -> str:
    lock = raiz / "render" / "package-lock.json"
    try:
        dados = json.loads(lock.read_text(encoding="utf-8"))
        return dados["packages"]["node_modules/remotion"]["version"]
    except (OSError, ValueError, KeyError):
        return "4.x"


def check_render_npm(amb: Ambiente) -> Requisito:
    explic = "Pacotes do render (Remotion), com `npm install` na pasta render/ (cerca de 300 MB)."
    if amb.raiz is None:
        return Requisito("render-npm", OPCIONAL, "", False, PROJETO, f"{explic} {SEM_RAIZ}")
    render = amb.raiz / "render"
    versao = _versao_remotion(amb.raiz)
    if (render / "node_modules" / "remotion").is_dir():
        return Requisito("render-npm", OK, f"remotion {versao}", False, PROJETO, explic,
                         pasta=str(render))
    return Requisito("render-npm", OPCIONAL, "", False, PROJETO,
                     f"{explic} Remotion {versao}. Precisa do Node antes.",
                     [["npm", "install"]], str(render))


def check_chrome(amb: Ambiente) -> Requisito:
    explic = ("Chrome Headless Shell que o Remotion usa para desenhar o vídeo (cerca de 100 MB, "
              "em render/node_modules/.remotion/). Baixa sozinho no primeiro render.")
    if amb.raiz is None:
        return Requisito("chrome-headless", OPCIONAL, "", False, DOWNLOAD, f"{explic} {SEM_RAIZ}")
    render = amb.raiz / "render"
    if (render / "node_modules" / ".remotion" / "chrome-headless-shell").is_dir():
        return Requisito("chrome-headless", OK, "baixado", False, DOWNLOAD, explic,
                         pasta=str(render))
    return Requisito("chrome-headless", OPCIONAL, "", False, DOWNLOAD,
                     explic + " Precisa do render-npm antes.",
                     [["npx", "remotion", "browser", "ensure"]], str(render))


def check_licenca_remotion(amb: Ambiente) -> Requisito:
    return Requisito(
        "licenca-remotion", OPCIONAL, "", False, SEU,
        "O Remotion é grátis para uso pessoal e para empresas de até 3 pessoas; acima disso, "
        "a empresa precisa da licença paga (https://www.remotion.dev/license). Quem decide e "
        "aceita é você; este script não aceita nada.")


def check_openrouter(amb: Ambiente) -> Requisito:
    return Requisito(
        "openrouter", OPCIONAL, "", False, SEU,
        "Opcional. Só para automação sem agente (comandos suggest e script). Se quiser, crie "
        "a chave no OpenRouter e ponha em OPENROUTER_API_KEY no arquivo .env (copie de "
        ".env.example). Este script não lê nem grava chaves.")


CHECKS: list[Callable[[Ambiente], Requisito]] = [
    check_uv, check_python, check_ffmpeg, check_libass,
    check_extra_transcribe, check_extra_voice, check_extra_vision,
    check_whisper_modelo, check_demucs_modelo,
    check_node, check_render_npm, check_chrome,
    check_licenca_remotion, check_openrouter,
]


def checar(amb: Ambiente) -> list[Requisito]:
    return [c(amb) for c in CHECKS]


def falta_obrigatorio(reqs: list[Requisito]) -> bool:
    return any(r.obrigatorio and r.estado != OK for r in reqs)


# ---------- saída ----------

def comando_texto(r: Requisito) -> str:
    if not r.comandos:
        return "veja a explicação" if r.estado != OK else ""
    cmds = " && ".join(" ".join(_citar(a) for a in c) for c in r.comandos)
    return f"(em {r.pasta}) {cmds}" if r.pasta else cmds


def _citar(arg: str) -> str:
    return f'"{arg}"' if re.search(r"[\s;()'>]", arg) else arg


def em_tabela(reqs: list[Requisito]) -> str:
    """Tabela Markdown com uma linha por requisito e um rodapé com o próximo passo."""
    linhas = ["| Requisito | Estado | Versão | Como resolver |", "|---|---|---|---|"]
    for r in reqs:
        resolver = "" if r.estado == OK else comando_texto(r)
        linhas.append(f"| {r.nome} | {r.estado} | {r.versao or '-'} | {resolver or '-'} |")
    rodape = ("Falta requisito obrigatório: rode o `instalar` deste mesmo script."
              if falta_obrigatorio(reqs) else "Todos os obrigatórios estão ok.")
    return "\n".join([*linhas, "", rodape])


def em_json(reqs: list[Requisito]) -> str:
    return json.dumps({"ok": not falta_obrigatorio(reqs), "requisitos": [asdict(r) for r in reqs]},
                      ensure_ascii=False, indent=2)


# ---------- instalar ----------

def instalar(amb: Ambiente, sim: bool, interativo: bool,
             perguntar: Callable[[str], str] = input,
             saida: Callable[[str], None] = print,
             executor: Callable[[list[str], str | None], tuple[int, str]] | None = None) -> int:
    """Mostra e roda os comandos do que falta. Idempotente: o que já está ok é pulado.

    A checagem usa o executor do ambiente (silencioso); a instalação usa `executor`.
    """
    executor = executor or amb.executar
    pendentes = [r for r in checar(amb) if r.estado != OK]
    if not pendentes:
        saida("Nada a instalar: todos os requisitos estão ok.")
        return 0
    falhou = False
    for r in pendentes:
        saida(f"\n[{r.estado}] {r.nome}: {r.explicacao}")
        if r.tipo == SEU or not r.comandos:
            saida("    Este item é seu: nada é rodado por aqui.")
            continue
        saida(f"    Comando: {comando_texto(r)}")
        if not sim:
            if not interativo:
                continue
            if perguntar("    Rodar agora? [s/N] ").strip().lower() not in ("s", "sim"):
                saida("    Pulado.")
                continue
        for cmd in r.comandos:
            codigo, texto = executor(cmd, r.pasta or None)
            if codigo != 0:
                saida(f"    Falhou (código {codigo}): {_primeira_linha(texto)}")
                falhou = True
                break
        else:
            saida("    Feito.")
    if not sim and not interativo:
        saida("\nNada foi rodado (sem terminal para perguntar). Rode os comandos acima ou use "
              "`instalar --sim` para rodar todos sem perguntar.")
    return 1 if falhou else 0


def _rodar_visivel(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    """Na instalação, a saída do programa aparece na tela (downloads demoram)."""
    try:
        return subprocess.run(args, cwd=cwd, check=False).returncode, ""
    except OSError as e:
        return 127, str(e)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Confere e instala os requisitos do reel-studio.")
    sub = p.add_subparsers(dest="comando", required=True)
    c = sub.add_parser("checar", help="mostra cada requisito; código 1 se faltar obrigatório")
    c.add_argument("--json", action="store_true", help="saída em JSON")
    i = sub.add_parser("instalar", help="mostra e roda os comandos do que falta")
    i.add_argument("--sim", action="store_true", help="roda sem perguntar item a item")
    for s in (c, i):
        s.add_argument("--raiz", help="pasta do reel-studio (padrão: detecta)")
    args = p.parse_args(argv)
    amb = Ambiente(raiz=achar_raiz(args.raiz))
    if args.comando == "checar":
        reqs = checar(amb)
        print(em_json(reqs) if args.json else em_tabela(reqs))
        return 1 if falta_obrigatorio(reqs) else 0
    return instalar(amb, args.sim, sys.stdin.isatty(), executor=_rodar_visivel)


if __name__ == "__main__":
    sys.exit(main())
