"""F4 — preparo da simulação: espera medida pelas funções do motor × contrafactual regular, com resposta conhecida."""
import importlib.util
import json
import pathlib

import numpy as np
import pandas as pd
import pytest
from scipy.spatial import cKDTree

from core.frota import regularidade as R

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PREP = _modulo("simulacao_preparar", "scripts/simulacao_preparar.py")
APP = _modulo("simulacao_app", "app/simulacao.py")
INI = 14 * 3600


def _cenario(intervalos_min, n_atual=10, n_rec=12):
    """Linha reta de 6 km (ida e volta); ônibus a 10 m/s; partidas da ida com os intervalos dados; GPS a cada 30 s."""
    L, v = 6000.0, 10.0
    s = np.arange(0, L, R.PASSO_M)
    trac = {("T1-10", 1): (cKDTree(np.c_[s, 0 * s]), s), ("T1-10", 2): (cKDTree(np.c_[L - s, 0 * s]), s)}
    partidas = INI + 60 * np.r_[0, np.cumsum(intervalos_min)]
    linhas = []
    for p, t0 in enumerate(partidas):
        t = np.arange(t0, t0 + L / v + 1, 30)
        x = v * (t - t0)
        linhas.append(pd.DataFrame({"c": "T1-10", "sl": 1, "p": 1000 + p, "t": t,
                                    "lat": R.LAT0 + 0 * x, "lon": x / R.KX + R.LON0}))
    pos = pd.concat(linhas, ignore_index=True)
    fim = int(partidas[-1] + L / v + 60)
    inst = np.arange(INI, fim + 1, 30.0)
    prog = pd.DataFrame({"route_id": "T1-10", "sl": [1, 1], "hora": [14, 15], "h_prog": [6.0, 6.0]})
    rea = pd.DataFrame({"c": ["T1-10"], "lote": ["X1"], "empresa_lote": ["Teste"], "passageiros_dia": [1000.0],
                        "ciclo_min": [20.0], "n_atual": [n_atual], "n_recomendada": [n_rec], "no_otimo": [True],
                        "delta": [n_rec - n_atual], "cv": [np.nan]})
    dur = {("T1-10", 1): 10.0, ("T1-10", 2): 10.0}
    return PREP.preparar("X1", pos, inst, trac, prog, dur, rea, "dia-teste", INI, fim)


def test_irregular_espera_medida_e_contrafactual_a_mao():
    # 12 intervalos alternando 2 e 10 min: AWT = (4 + 100) / (2 * 12) = 4,333; regular com a mesma vazão = 6 / 2 = 3
    sim = _cenario([2, 10] * 6)
    l, r = sim["linhas"][0], sim["resumo"]
    assert l["espera_real"] == pytest.approx(104 / 24, abs=0.01)
    assert l["espera_regular"] == pytest.approx(3.0, abs=0.01)
    assert l["espera_realoc"] == pytest.approx(3.0 * 10 / 12, abs=0.01)      # cenário B: intervalo × n_atual / n_rec
    assert r["ganho_regularizar"] == pytest.approx(104 / 24 - 3, abs=0.01)
    assert len(sim["onibus"]) == 13 and l["sentidos"] == [1, 2] and l["frac_sentido"] == [0.5, 0.5]
    assert all(0 <= p[4] <= 6000 for o in sim["onibus"] for p in o["pts"])     # metros no traçado


def test_regular_nao_ganha_nada_ao_regularizar():
    sim = _cenario([6] * 12, n_atual=10, n_rec=10)
    assert sim["resumo"]["ganho_regularizar"] == pytest.approx(0, abs=0.01)
    assert sim["resumo"]["ganho_realocar"] == pytest.approx(0, abs=1e-9)
    json.dumps(sim)                                                             # o arquivo grava sem erro


def test_app_so_serve_arquivo_da_pasta(tmp_path, monkeypatch):
    monkeypatch.setattr(APP, "PASTA", tmp_path)
    (tmp_path / "sim_d_X1_1400_1500.json").write_text(json.dumps(
        {"lote": "X1", "empresa": "Teste", "dia": "d", "janela": [0, 3600], "gerado_em": "-", "resumo": {}}), encoding="utf-8")
    assert [a["lote"] for a in APP.lista()["arquivos"]] == ["X1"]
    with pytest.raises(KeyError):
        APP.carregar("../../.env")
