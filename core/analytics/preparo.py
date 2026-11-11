"""Preparo da OD 2017 para os modelos: quem usa ônibus para trabalhar e quanto a viagem dura.

Cada filtro é uma etapa nomeada do funil, para que a limpeza seja auditável:
o relatório mostra quantas linhas saíram em cada passo e por quê.
"""
import numpy as np
import pandas as pd

from core.config import MODO_ONIBUS, MUNI_SP, OD_CSV

BRUTAS = ["renda_fa", "qt_auto", "idade", "distancia", "duracao", "vinc1", "ocup1", "no_morad"]
COLUNAS = BRUTAS + ["id_pess", "id_fam", "n_viag", "muni_o", "muni_d", "motivo_d", "cd_ativi",
                    "modoprin", "cd_renfa", "h_saida", "modo1", "modo2", "modo3", "modo4"]
HORAS_PICO = (6, 7, 8, 17, 18, 19)
OCUPACAO_MINIMA = 100      # grupos de ocupação menores que isso viram "outras" (11)

ETAPAS = [
    ("origem e destino no município de SP", lambda d: (d.muni_o == MUNI_SP) & (d.muni_d == MUNI_SP)),
    ("motivo no destino é trabalho", lambda d: d.motivo_d.isin((1, 2, 3))),
    ("pessoa com trabalho regular", lambda d: d.cd_ativi == 1),
    ("sem nulos nos preditores e renda > 0", lambda d: d[BRUTAS].notna().all(axis=1) & (d.renda_fa > 0)),
    ("primeira viagem a trabalho de cada pessoa",
     lambda d: ~d.sort_values("n_viag").duplicated("id_pess").reindex(d.index)),
]


def funil(df: pd.DataFrame, etapas=ETAPAS):
    """Aplica os filtros em ordem. Devolve a base filtrada e a tabela de linhas por etapa."""
    linhas = [("viagens registradas na OD", len(df))]
    for nome, filtro in etapas:
        df = df[filtro(df)]
        linhas.append((nome, len(df)))
    t = pd.DataFrame(linhas, columns=["etapa", "linhas"])
    return df, t.assign(removidas=-t.linhas.diff().fillna(0).astype(int))


def derivar(d: pd.DataFrame) -> pd.DataFrame:
    """Variáveis do modelo a partir das colunas brutas."""
    raras = d.ocup1.map(d.ocup1.value_counts()) < OCUPACAO_MINIMA
    return d.assign(
        usa_onibus=(d.modoprin == MODO_ONIBUS).astype(int),
        distancia_km=d.distancia / 1000,
        renda_pc=d.renda_fa / d.no_morad,
        log_renda_pc=np.log(d.renda_fa / d.no_morad),
        clt=(d.vinc1 == 1).astype(int),
        pico=d.h_saida.isin(HORAS_PICO).astype(int),
        ocupacao=d.ocup1.mask(raras, 11).astype(int),
        renda_declarada=(d.cd_renfa == 1).astype(int),
        n_trechos=d[["modo1", "modo2", "modo3", "modo4"]].notna().sum(axis=1),
    )


def base_trabalho(caminho=OD_CSV):
    """Uma linha por trabalhador (viagem de ida ao trabalho dentro de SP) e o funil da limpeza."""
    od = pd.read_csv(caminho, sep=";", usecols=COLUNAS)
    base, etapas = funil(od[od.modo1.notna()])
    return derivar(base), etapas


def sem_outliers(df: pd.DataFrame, colunas) -> pd.DataFrame:
    """Remove linhas fora de [Q1 - 1,5 IQR, Q3 + 1,5 IQR] em qualquer das colunas."""
    q1, q3 = df[colunas].quantile(0.25), df[colunas].quantile(0.75)
    folga = 1.5 * (q3 - q1)
    return df[df[colunas].ge(q1 - folga).all(axis=1) & df[colunas].le(q3 + folga).all(axis=1)]
