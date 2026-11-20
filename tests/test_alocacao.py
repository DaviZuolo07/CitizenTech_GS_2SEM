"""M2 (alocação por lote) e M1 (espera com intervalo irregular)."""
import numpy as np
import pandas as pd

from core.frota import regularidade as R
from core.frota.alocacao import alocar, realocar


def test_raiz_quadrada_caso_a_mao():
    # demanda 4:1, mesmo ciclo, 10 ônibus: n ∝ √(d·t) = 2:1 -> ótimo inteiro 7 e 3 (força bruta)
    n = alocar(np.array([5, 5]), np.array([4.0, 1.0]), 1.0, perda_max=1.0)
    melhor = min(((i, 10 - i) for i in range(1, 10)), key=lambda x: 4 / x[0] + 1 / x[1])
    assert tuple(n) == melhor == (7, 3)


def test_piso_e_conservacao():
    rng = np.random.default_rng(0)
    for _ in range(300):
        k = rng.integers(2, 10)
        n0, a = rng.integers(1, 30, k), rng.random(k) * 100
        for m in (1.0, 0.5):
            n = alocar(n0, a, m, 0.2)
            assert n.sum() == n0.sum() and (n >= np.ceil(0.8 * n0 - 1e-9)).all()


def test_nada_cruza_lote_e_linha_rara_fica_fixa():
    tab = pd.DataFrame({"c": list("abcd"), "lote": ["L1", "L1", "L2", "L2"], "passageiros_dia": [9000, 100, 50, 5000],
                        "ciclo_min": [100, 100, 100, 600], "n_atual": [10, 10, 10, 10]})
    r = realocar(tab, 0.2, h_max=15)
    assert r.groupby("lote").n_recomendada.sum().eq(r.groupby("lote").n_atual.sum()).all()
    assert r.set_index("c").loc["d", "n_recomendada"] == 10      # intervalo 60 min: fora do ótimo
    assert r.set_index("c").loc["a", "n_recomendada"] > 10


def test_espera_irregular_m1():
    # intervalos 2 e 18 min (média 10): AWT = (4 + 324) / (2 · 20) = 8,2 min, contra 5 se fossem regulares
    h = pd.DataFrame({"c": "x", "sl": 1, "hora": 14, "h": [2.0, 18.0] * 5, "h_prog": 10.0})
    r = R.regularidade(h).iloc[0]
    assert abs(r.espera_real - 8.2) < 1e-9 and abs(r.espera_excessiva - 3.2) < 1e-9 and r.comboio == 0.5


def test_decomposicao_ewt_a_mao():
    """Intervalos alternando 2 e 10 min, programado 5: AWT = 104·6/(2·72) = 4,333; metade do intervalo médio = 3;
    SWT = 2,5. Irregularidade 1,333 + falta de ônibus 0,5 = EWT 1,833."""
    import pandas as pd
    from core.frota import regularidade as R
    h = pd.DataFrame({"c": "X", "sl": 1, "hora": 14, "h": [2.0, 10.0] * 6, "h_prog": 5.0})
    r = R.regularidade(h).iloc[0]
    assert abs(r.espera_excessiva - 1.833) < 1e-3
    assert abs(r.irregularidade - 1.333) < 1e-3 and abs(r.falta_onibus - 0.5) < 1e-3
