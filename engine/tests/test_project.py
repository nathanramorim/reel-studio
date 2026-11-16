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
