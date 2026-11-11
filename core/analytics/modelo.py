"""Treino e avaliação da regressão logística P(usa ônibus | perfil).

Regras: a família nunca é dividida entre treino e teste (moradores da mesma casa
compartilham renda e carro), e o limiar de decisão é escolhido só com o treino.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn import metrics
from sklearn.model_selection import StratifiedGroupKFold

ALVO, GRUPO = "usa_onibus", "id_fam"


def _dobras(df: pd.DataFrame, k: int, semente: int):
    return StratifiedGroupKFold(k, shuffle=True, random_state=semente).split(df, df[ALVO], df[GRUPO])


def separar(df: pd.DataFrame, semente=42):
    """Treino (80%) e teste (20%), estratificados pelo alvo e agrupados por família."""
    treino, teste = next(_dobras(df, 5, semente))
    return df.iloc[treino], df.iloc[teste]


def ajustar(formula: str, dados: pd.DataFrame):
    """Regressão logística por máxima verossimilhança (sem regularização)."""
    return smf.logit(formula, dados).fit(disp=0)


def prob_validacao_cruzada(formula: str, treino: pd.DataFrame, k=5, semente=42) -> pd.Series:
    """Probabilidade de cada linha do treino, prevista por um modelo que não a viu."""
    p = pd.Series(np.nan, index=treino.index)
    for a, b in _dobras(treino, k, semente):
        p.iloc[b] = ajustar(formula, treino.iloc[a]).predict(treino.iloc[b])
    return p


def melhor_limiar(y, p) -> float:
    """Limiar de decisão que maximiza o F1 (equilíbrio entre precisão e recall)."""
    grade = np.arange(0.05, 0.96, 0.01)
    return float(grade[np.argmax([metrics.f1_score(y, p >= t) for t in grade])])


def avaliar(y, p, limiar=0.5) -> dict:
    """Métricas de classificação no limiar dado, mais a AUC (que não depende do limiar)."""
    prev = p >= limiar
    return {"limiar": limiar, "acuracia": metrics.accuracy_score(y, prev),
            "precisao": metrics.precision_score(y, prev, zero_division=0),
            "recall": metrics.recall_score(y, prev), "f1": metrics.f1_score(y, prev),
            "auc": metrics.roc_auc_score(y, p)}


def matriz_confusao(y, p, limiar=0.5) -> pd.DataFrame:
    m = metrics.confusion_matrix(y, p >= limiar)
    return pd.DataFrame(m, index=["real: não usa", "real: usa"], columns=["previsto: não usa", "previsto: usa"])


def calibracao(y, p, faixas=10) -> pd.DataFrame:
    """Por faixa de probabilidade prevista: média prevista x proporção observada."""
    faixa = pd.qcut(p, faixas, labels=False, duplicates="drop")
    return pd.DataFrame({"prevista": p, "observada": y}).groupby(faixa).agg(
        prevista=("prevista", "mean"), observada=("observada", "mean"), n=("observada", "size"))
