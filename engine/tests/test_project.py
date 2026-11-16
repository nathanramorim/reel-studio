from reel_studio.core.project import Project


def test_project_cria_pasta_e_detecta_mudanca(tmp_path):
    video = tmp_path / "aula.mp4"
    video.write_bytes(b"conteudo-1")
    p = Project.open(video)
    assert p.dir.is_dir()
    marker = p.path("transcript.json")
    marker.write_text("{}")
    video.write_bytes(b"conteudo-2-bem-diferente")
    p2 = Project.open(video)
    assert not marker.is_file()
    assert p2.dir == p.dir


def test_open_text_cria_pasta_sem_exigir_video(tmp_path):
    p = Project.open_text("minha-ideia", base=tmp_path)
    assert p.video is None
    assert p.dir == (tmp_path / "reel-projects" / "minha-ideia").resolve()
    assert p.dir.is_dir()
    assert [x.name for x in tmp_path.iterdir()] == ["reel-projects"]


def test_open_text_nao_toca_fora_da_pasta(tmp_path):
    import pytest

    from reel_studio.core.errors import ReelError
    for ruim in ("../fora", "a/b", "/abs", "", "Maiusculo"):
        with pytest.raises(ReelError):
            Project.open_text(ruim, base=tmp_path)
    assert list(tmp_path.iterdir()) == []
