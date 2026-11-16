from reel_studio.core.suggest import normalize


def test_normalize_encaixa_nos_limites_do_segmento(transcript):
    hook = "Automatize em 3 passos"
    raw = {"clips": [{"start": 0.1, "end": 6.9, "hook": hook, "reason": "intro forte"}]}
    data = normalize(raw, transcript, min_s=5, max_s=60, max_clips=5)
    clip = data["clips"][0]
    assert clip["id"] == "clip-01"
    assert clip["start"] == 0.0
    assert clip["end"] == 7.0


def test_normalize_descarta_clip_curto_demais(transcript):
    raw = {"clips": [{"start": 0.0, "end": 1.0, "hook": "x"}]}
    data = normalize(raw, transcript, min_s=15, max_s=60, max_clips=5)
    assert data["clips"] == []


def test_normalize_respeita_max_clips(transcript):
    raw = {"clips": [
        {"start": 0.0, "end": 3.2, "hook": "a"},
        {"start": 3.2, "end": 7.0, "hook": "b"},
        {"start": 7.0, "end": 12.0, "hook": "c"},
    ]}
    data = normalize(raw, transcript, min_s=1, max_s=60, max_clips=2)
    assert len(data["clips"]) == 2


def test_prompt_nao_chama_rede(transcript):
    from reel_studio.core.suggest import prompt

    system, user = prompt(transcript, max_clips=3, min_s=10, max_s=60)
    assert "clips" in system
    assert "[0.0]" in user
