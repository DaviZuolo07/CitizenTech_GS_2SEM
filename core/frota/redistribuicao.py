"""Redistribuição da frota como transformação linear x -> T x.

T é coluna-estocástica (entradas >= 0, cada coluna soma 1), o que garante que a
frota total é preservada e que nenhuma área fica com valor negativo. T é montada
a partir do diagnóstico; uma vez fixada, a aplicação x -> T x é linear.
"""
import numpy as np


def maior_resto(pesos, total: int) -> np.ndarray:
    """Reparte `total` unidades inteiras na proporção dos pesos (método de Hamilton)."""
    if total == 0:
        return np.zeros(len(pesos), int)
    cotas = np.asarray(pesos, float) * total / np.sum(pesos)
    base = np.floor(cotas).astype(int)
    sobra = total - base.sum()
    base[np.argsort(base - cotas, kind="stable")[:sobra]] += 1
    return base


def alvo_proporcional(x, necessidade, perda_maxima=1.0) -> np.ndarray:
    """Frota-alvo inteira: mesma soma de x, proporcional à necessidade.

    Iguala a razão frota/necessidade entre as áreas. `perda_maxima` é a fração
    da frota que uma área pode ceder (piso de cobertura): quem ficaria abaixo do
    piso fica no piso, e o restante é repartido proporcionalmente entre as demais.
    """
    x, nec = np.asarray(x), np.asarray(necessidade, float)
    if nec.sum() == 0:
        return x.copy()
    piso = np.ceil((1 - perda_maxima) * x).astype(int)
    preso, ideal = np.zeros(len(x), bool), piso.astype(float)
    while not preso.all():
        ideal = nec * (x.sum() - piso[preso].sum()) / nec[~preso].sum()
        novos = ~preso & (ideal < piso - 1e-9)
        if not novos.any():
            break
        preso |= novos
    excesso = np.where(preso, 0, ideal - piso)
    return piso + maior_resto(excesso, int(x.sum() - piso.sum()))


def matriz_redistribuicao(x, alvo) -> np.ndarray:
    """Matriz T com T @ x == alvo.

    Coluna de quem cede: fica com alvo/x e cede o resto aos que têm falta, na
    proporção da falta de cada um. Coluna de quem não cede: vetor canônico.
    """
    x, alvo = np.asarray(x, float), np.asarray(alvo, float)
    sobra, falta = np.clip(x - alvo, 0, None), np.clip(alvo - x, 0, None)
    if sobra.sum() == 0:
        return np.eye(len(x))
    cedido = np.divide(sobra, x, out=np.zeros_like(x), where=x > 0)
    T = np.outer(falta / falta.sum(), cedido)
    T[np.diag_indices_from(T)] += 1 - cedido
    return T


def verificar(T, x, alvo, tol=1e-9) -> dict:
    """Checagens numéricas das propriedades provadas no relatório."""
    y = T @ np.asarray(x, float)
    return {"colunas_somam_1": bool(np.allclose(T.sum(axis=0), 1, atol=tol)),
            "sem_negativos": bool((T >= 0).all() and (y >= -tol).all()),
            "preserva_total": bool(np.isclose(y.sum(), np.sum(x), atol=tol)),
            "atinge_alvo_inteiro": bool(np.allclose(y, alvo, atol=1e-6))}
