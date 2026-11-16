from reel_studio.core.frames import Region, track


def _r(cx, cy):
    return Region(cx - 0.2, cy - 0.15, 0.4, 0.3)


def test_janelas_regiao_estavel_nao_gera_troca():
    steps = track([_r(0.5, 0.5), _r(0.52, 0.51), _r(0.49, 0.5)], [0.0, 5.0, 10.0])
    assert len(steps) == 1 and steps[0][0] == 0.0


def test_janelas_deslocamento_grande_gera_troca():
    steps = track([_r(0.3, 0.3), _r(0.31, 0.3), _r(0.7, 0.6)], [0.0, 5.0, 10.0])
    assert [t for t, _ in steps] == [0.0, 10.0]


def test_janelas_sem_atividade_herda_a_anterior():
    steps = track([None, _r(0.4, 0.4), None], [0.0, 5.0, 10.0])
    assert len(steps) == 1 and steps[0][0] == 0.0
