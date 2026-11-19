"""Painel do gestor (F3): regularidade medida e realocação por lote, a partir das saídas de scripts/motor_empresa.py.

A realocação é recalculada em memória com os controles da tela (perda máxima por linha, que é o piso de cobertura, e corte de intervalo), pela mesma
função do motor (core.frota.alocacao.realocar). O arquivo realocacao_linha.csv não é alterado: o F4 lê dele a
recomendação padrão (n_atual, n_recomendada).
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import PERDA_MAXIMA, PROC  # noqa: E402
from core.frota import alocacao as A  # noqa: E402

LIMITE_EWT = 15  # min; o mesmo de core.frota.regularidade (não importado para não puxar scipy no servidor)
ENTRADA = ["c", "lote", "empresa_lote", "passageiros_dia", "ciclo_min", "n_media", "n_atual", "cv"]
_cache = {}


def _ler(nome: str) -> pd.DataFrame:
    """CSV do motor, relido só quando o arquivo muda (o motor pode rodar de novo com o servidor no ar)."""
    p = PROC / nome
    t = p.stat().st_mtime
    if _cache.get(nome, (None,))[0] != t:
        _cache[nome] = (t, pd.read_csv(p))
    return _cache[nome][1]


def _registros(df: pd.DataFrame) -> list:
    return json.loads(df.round(3).to_json(orient="records", force_ascii=False))  # NaN vira null


def resumo_motor() -> dict:
    return json.loads((PROC / "resumo_motor.json").read_text(encoding="utf-8"))


def regularidade() -> dict:
    """Por linha e por lote: espera real × programada, espera excessiva (só intervalo programado <= 15 min) e comboio."""
    lin = _ler("regularidade_linha.csv").copy()
    lin.loc[~lin.alta_frequencia, "espera_excessiva"] = None      # Londres: EWT só vale em linha frequente
    lin = lin.sort_values(["alta_frequencia", "espera_excessiva"], ascending=[False, False])
    cols = ["c", "lote", "empresa_lote", "intervalos", "h_media", "h_prog", "cv", "espera_real", "espera_prog",
            "espera_excessiva", "comboio", "alta_frequencia", "passageiros_dia"]
    lot = _ler("regularidade_lote.csv").sort_values("espera_excessiva", ascending=False)
    r = resumo_motor()
    return {"coleta": r["coleta"], "resumo": r["regularidade"], "limite_ewt": LIMITE_EWT,
            "lotes": _registros(lot), "linhas": _registros(lin[cols])}


def realocacao(lote: str = "", perda: float = PERDA_MAXIMA, h_max: float = LIMITE_EWT) -> dict:
    """Frota atual × recomendada por linha dentro do lote, com os controles da tela. Sem lote: o que mais poupa."""
    perda = min(max(float(perda), 0.0), 0.5)
    h_max = min(max(float(h_max), 5.0), 30.0)
    rea = A.realocar(_ler("realocacao_linha.csv")[ENTRADA], perda, h_max)
    lotes = A.resumir_lotes(rea).sort_values("horas_espera_poupadas_dia", ascending=False)
    if lote not in lotes.index:
        lote = lotes.index[0] if len(lotes) else ""
    linhas = rea[rea.lote == lote].assign(intervalo_atual=lambda d: d.ciclo_min / d.n_atual,
                                          intervalo_depois=lambda d: d.ciclo_min / d.n_recomendada)
    linhas = linhas.sort_values(["no_otimo", "delta"], ascending=[False, False])
    cols = ["c", "empresa_lote", "passageiros_dia", "ciclo_min", "n_atual", "n_recomendada", "delta", "no_otimo",
            "intervalo_atual", "intervalo_depois", "espera_antes", "espera_depois", "espera_depois_k23"]
    return {"parametros": {"perda": perda, "h_max": h_max, "padrao": {"perda": PERDA_MAXIMA, "h_max": LIMITE_EWT}},
            "coleta": resumo_motor()["coleta"], "total": A.resumir_total(rea),
            "lotes": _registros(lotes.reset_index()), "lote": lote, "linhas": _registros(linhas[cols])}
