from reel_studio.core import sensitive


def test_detecta_chaves_tokens_e_emails():
    assert "chave AWS" in sensitive.scan("AKI" + "AABCDEFGHIJKLMNOP")
    assert "chave sk-" in sensitive.scan("sk-" + "a1" * 15)
    assert "token GitHub" in sensitive.scan("ghp_" + "x" * 36)
    assert "e-mail" in sensitive.scan("fale com ana@exemplo.com.br")
    assert "segredo atribuído" in sensitive.scan("password = hunter22222")


def test_texto_limpo_nao_gera_aviso():
    assert sensitive.scan("Automatize o reel com um comando só") == []
    assert sensitive.warnings([{"narration": "Tudo roda local", "text": "Sem nuvem"}]) == []


def test_nada_sensivel_e_logado():
    segredo = "ghp_" + "Z" * 36
    avisos = sensitive.warnings([{"narration": segredo, "text": "x"}], share=segredo)
    assert avisos and all(segredo not in a for a in avisos)


def test_media_sempre_avisa():
    avisos = sensitive.warnings([{"narration": "", "media": {"source": {"start": 0, "end": 2}}}])
    assert sensitive.MEDIA_WARNING in avisos


def test_transcricao_varrida():
    t = {"segments": [{"text": "meu e-mail é ana@exemplo.com"}]}
    assert any("transcrição" in a for a in sensitive.warnings([], t))
