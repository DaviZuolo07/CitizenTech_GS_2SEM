import numpy as np
import pytest

from core.frota.redistribuicao import (alvo_proporcional, maior_resto,
                                       matriz_redistribuicao, verificar)


def test_maior_resto_soma_exata_e_proporcional():
    r = maior_resto([1, 1, 1], 10)
    assert r.sum() == 10 and sorted(r) == [3, 3, 4]
    assert list(maior_resto([2, 1, 1], 8)) == [4, 2, 2]


@pytest.mark.parametrize("semente", range(50))
def test_propriedades_em_vetores_aleatorios(semente):
    rng = np.random.default_rng(semente)
    k = rng.integers(2, 40)
    x = rng.integers(0, 500, k)
    x[0] += 1                       # frota total positiva
    necessidade = rng.random(k) + 0.01
    perda = rng.choice([0.0, 0.2, 1.0])
    alvo = alvo_proporcional(x, necessidade, perda_maxima=perda)
    T = matriz_redistribuicao(x, alvo)
    assert alvo.sum() == x.sum() and (alvo >= np.ceil((1 - perda) * x)).all()
    assert all(verificar(T, x, alvo).values())


def test_sem_desequilibrio_devolve_identidade():
    x = np.array([10, 20, 30])
    assert np.array_equal(matriz_redistribuicao(x, x), np.eye(3))


def test_caso_do_enunciado_mmc():
    """Sistema do Relatório I + necessidade do Relatório II (ceil(passageiros / 40))."""
    A = np.array([[1, 1, 1, 1], [1, 2, 0, 1], [0, 1, 2, 0], [1, 0, 1, 2]])
    x = np.linalg.solve(A, [72, 76, 52, 76])
    necessidade = np.ceil(np.array([560, 760, 720, 840]) / 40)
    alvo = alvo_proporcional(np.rint(x).astype(int), necessidade)
    T = matriz_redistribuicao(x, alvo)
    assert np.allclose(x, np.rint(x)) and (x >= 0).all()
    assert np.array_equal(alvo, necessidade)          # necessidade total == frota total
    assert all(verificar(T, x, alvo).values())


def test_piso_de_cobertura_limita_a_perda():
    x = np.array([100, 100, 100])
    alvo = alvo_proporcional(x, [1, 1, 10], perda_maxima=0.2)
    assert list(alvo) == [80, 80, 140]
    assert list(alvo_proporcional(x, [1, 1, 10], perda_maxima=0.0)) == [100, 100, 100]
