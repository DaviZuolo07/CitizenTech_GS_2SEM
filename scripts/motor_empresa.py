"""Motor por lote (F1+F2): regularidade medida no Olho Vivo e frota recomendada por linha dentro de cada lote.

Entradas: data/olhovivo/<dia>/ (coletor), GTFS, planilha mensal de passageiros da SPTrans (data/sptrans/).
Saídas em data/processed/: regularidade_linha.csv, regularidade_lote.csv, realocacao_linha.csv,
realocacao_lote.csv, resumo_motor.json.
Uso: python scripts/motor_empresa.py [pasta_da_coleta]   (padrão: o dia mais recente em data/olhovivo)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import GTFS_ZIP, PERDA_MAXIMA, PROC, RAIZ  # noqa: E402
from core.frota import alocacao as A, regularidade as R  # noqa: E402

PLANILHA, DIAS_PLANILHA = RAIZ / "data/sptrans/consolidado_setembro_2026.xlsx", 30


def main(pasta: Path) -> None:
    trac, prog, dur = R.ler_gtfs(GTFS_ZIP)
    pos, instantes, frota = R.ler_coleta(pasta)
    dem = A.demanda_planilha(PLANILHA, DIAS_PLANILHA)

    # F1 — regularidade por linha e por lote
    reg = R.regularidade(R.intervalos(R.passagens(pos, trac), instantes, prog)).merge(dem, on="c", how="left")
    reg.to_csv(PROC / "regularidade_linha.csv", index=False)
    alta = reg[reg.alta_frequencia]
    reg_lote = reg.groupby("lote").apply(lambda g: pd.Series({
        "empresa": g.empresa_lote.mode().iat[0], "linhas_medidas": len(g), "intervalos": g.intervalos.sum(),
        "cv_mediano": g.cv.median(), "comboio": A.media(g.comboio, g.intervalos),
        "espera_real": A.media(g.espera_real, g.passageiros_dia), "espera_prog": A.media(g.espera_prog, g.passageiros_dia)}),
        include_groups=False)
    reg_lote["espera_excessiva"] = alta.groupby("lote").apply(
        lambda g: A.media(g.espera_excessiva, g.passageiros_dia), include_groups=False)
    for col in ("irregularidade", "falta_onibus"):
        reg_lote[col] = alta.groupby("lote").apply(lambda g: A.media(g[col], g.passageiros_dia), include_groups=False)
    reg_lote.round(3).to_csv(PROC / "regularidade_lote.csv")

    # F2 — frota por linha dentro do lote (M2)
    ciclo = dur.groupby("route_id").duracao_min.sum().rename("ciclo_min")
    tab = (A.frota_observada(frota).to_frame().join(ciclo).reset_index(names="c")
           .merge(dem, on="c").merge(reg[["c", "cv"]], on="c", how="left"))
    tab["n_atual"] = tab.n_media.round().astype(int)
    tab = tab[(tab.n_atual >= 1) & (tab.ciclo_min > 0) & (tab.passageiros_dia > 0)]
    rea = A.realocar(tab, PERDA_MAXIMA, R.LIMITE_EWT)
    rea.round(3).to_csv(PROC / "realocacao_linha.csv", index=False)
    lote = A.resumir_lotes(rea)
    lote.round(3).to_csv(PROC / "realocacao_lote.csv")

    resumo = {
        "coleta": {"pasta": str(Path(pasta).name), "inicio_h": round(instantes.min() / 3600, 2),
                   "fim_h": round(instantes.max() / 3600, 2), "instantes": len(instantes)},
        "regularidade": {"linhas_medidas": len(reg), "intervalos": int(reg.intervalos.sum()),
                         "espera_excessiva_media_min": round(A.media(alta.espera_excessiva, alta.passageiros_dia), 3),
                         "irregularidade_min": round(A.media(alta.irregularidade, alta.passageiros_dia), 3),
                         "falta_onibus_min": round(A.media(alta.falta_onibus, alta.passageiros_dia), 3),
                         # ônibus que passaram a menos que o programado: 1 − intervalo programado / intervalo medido
                         "onibus_a_menos_pct": round(100 * (1 - A.media(alta.h_prog, alta.passageiros_dia)
                                                             / A.media(alta.h_media, alta.passageiros_dia)), 1),
                         "onibus_a_menos_mediana_pct": round(100 * float((1 - alta.h_prog / alta.h_media).median()), 1),
                         "comboio_pct": round(100 * A.media(reg.comboio, reg.intervalos), 1)},
        "realocacao": {**A.resumir_total(rea), "h_max_min": R.LIMITE_EWT, "perda_maxima": PERDA_MAXIMA},
    }
    (PROC / "resumo_motor.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    dias = sorted(p for p in (RAIZ / "data/olhovivo").glob("20*") if p.is_dir())
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else dias[-1])
