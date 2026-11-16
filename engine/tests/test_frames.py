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


# --- região por densidade (feat-03-10) ---------------------------------------------------------
import pytest  # noqa: E402

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from reel_studio.core import frames  # noqa: E402

FW, FH = 480, 300
RATIO = 1080 / 920


def _quadros(retangulos, n=4):
    """n quadros cinza que alternam 0/255 dentro dos retângulos (x0, y0, x1, y1) em pixels."""
    out = []
    for i in range(n):
        q = np.zeros((FH, FW), dtype="uint8")
        if i % 2:
            for x0, y0, x1, y1 in retangulos:
                q[y0:y1, x0:x1] = 255
        out.append(q)
    return out


def _bgr(gray):
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def test_densidade_metade_direita_escolhe_janela_de_50_por_cento():
    r = frames._activity(cv2, _quadros([(300, 60, 460, 220)]))
    assert r is not None and r.w == pytest.approx(0.5)
    assert r.x + r.w == pytest.approx(1.0) and r.x > 0.45


def test_densidade_atividade_em_instantes_diferentes_gera_troca():
    esq = _quadros([(20, 60, 180, 220)])
    dir_ = _quadros([(300, 60, 460, 220)])
    quadros = [_bgr(g) for g in esq + dir_]
    analise = frames._analyze_frames(cv2, quadros, 12.0)
    assert len(analise.steps) == 2
    assert analise.steps[1][0] >= frames.MIN_INTERVAL
    assert analise.steps[0][1].x < analise.steps[1][1].x


def test_densidade_ponto_isolado_nao_expande_a_regiao():
    r = frames._activity(cv2, _quadros([(20, 60, 180, 220), (440, 100, 446, 106)]))
    assert r is not None and r.w == pytest.approx(0.5)


def test_densidade_dock_e_barra_de_menu_sao_ignorados():
    assert frames._activity(cv2, _quadros([(100, 285, 400, 300)])) is None
    assert frames._activity(cv2, _quadros([(100, 0, 400, 8)])) is None


def test_densidade_atividade_espalhada_devolve_fit():
    assert frames._activity(cv2, _quadros([(0, 40, 480, 260)])) is None


def test_proporcao_regiao_tem_a_proporcao_da_faixa_e_cabe_no_quadro():
    for ret in ([(20, 60, 180, 220)], [(100, 40, 400, 260)], [(300, 60, 460, 220)]):
        r = frames._activity(cv2, _quadros(ret))
        assert r is not None
        assert abs(r.w * FW - RATIO * r.h * FH) <= 1
        assert r.x >= 0 and r.y >= 0 and r.x + r.w <= 1 + 1e-9 and r.y + r.h <= 1 + 1e-9


REGIOES = {  # zoom_cortes.py (gravação 14.33.02): (w, h, [(x, y)]) em pixels de 2860x1776
    "clip-01": (1500, 1000, [(0, 0)]),
    "clip-02": (1430, 1190, [(0, 290), (1430, 200)]),
    "clip-03": (1430, 1190, [(1430, 200)]),
    "clip-04": (1430, 1190, [(1430, 200), (0, 420)]),
    "clip-05": (1900, 1300, [(0, 450), (200, 100), (960, 0)]),
}


@pytest.mark.parametrize("clip", REGIOES)
def test_oraculo_regiao_cobre_a_referencia_manual(clip):
    w, h, passos = REGIOES[clip]
    sx, sy = FW / 2860, FH / 1776
    for x, y in passos:
        ref = (round(x * sx), round(y * sy), round((x + w) * sx), round((y + h) * sy))
        r = frames._activity(cv2, _quadros([ref]))
        assert r is not None
        ix = max(0, min(ref[2], (r.x + r.w) * FW) - max(ref[0], r.x * FW))
        iy = max(0, min(ref[3], (r.y + r.h) * FH) - max(ref[1], r.y * FH))
        assert ix * iy >= 0.8 * (ref[2] - ref[0]) * (ref[3] - ref[1])


def test_intervalo_trocas_nunca_ficam_a_menos_de_3_segundos():
    regioes = [Region(0.0, 0.0, 0.5, 0.6), Region(0.5, 0.0, 0.5, 0.6)] * 6
    steps = track(regioes, [i * 1.0 for i in range(12)])
    tempos = [t for t, _ in steps]
    assert all(b - a >= 3.0 for a, b in zip(tempos, tempos[1:], strict=False))
    assert len(tempos) > 1
