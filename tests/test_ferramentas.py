import pytest

from core.agent.ferramentas import calcular_proximo_horario as proximo
from core.agent.ferramentas import consultar_fluxo, verificar_gratuidade


@pytest.mark.parametrize("linha, hora, dia, esperado", [
    ("714A-10", "06:05", "util", "06:08"),      # faixa de 8 em 8 min a partir das 06:00
    ("714A", "23:30", "util", "23:40"),         # última partida do dia entra
    ("318N-10", "04:00", "util", "05:10"),      # portaria: primeira partida deixou de ser 04:40
    ("502C-10", "06:10", "domingo", "06:20"),   # portaria: domingo de 20 em 20 min
    ("502c-10", "09:00", "sabado", "09:10"),
])
def test_proxima_partida(linha, hora, dia, esperado):
    assert proximo(linha, hora, dia)["proxima_partida"] == esperado


def test_linha_suprimida_no_domingo_e_feriado():
    assert proximo("714A-10", "10:00", "domingo")["opera"] is False
    assert proximo("714A-10", "10:00", "feriado")["opera"] is False


def test_erros_controlados():
    assert "erro" in proximo("999X-10", "10:00", "util")
    assert "erro" in proximo("714A-10", "dez horas", "util")
    assert "erro" in proximo("714A-10", "10:00", "ontem")
    assert "mensagem" in proximo("714A-10", "23:50", "util")
    assert "erro" in verificar_gratuidade(200, False, False, "util")
    assert "erro" in consultar_fluxo("Atlântida", "SE", 8)
    assert "erro" in consultar_fluxo("SE", "MOOCA", 30)


@pytest.mark.parametrize("idade, pcd, estudante, dia, gratuito", [
    (68, False, False, "sabado", True),     # 65+: todos os dias
    (62, False, False, "sabado", False),    # 60 a 64: só dia útil
    (62, False, False, "util", True),
    (20, False, True, "feriado", False),    # estudante: só dia letivo
    (20, False, True, "util", True),
    (30, True, False, "domingo", True),
    (30, False, False, "util", False),
])
def test_gratuidade(idade, pcd, estudante, dia, gratuito):
    assert verificar_gratuidade(idade, pcd, estudante, dia)["gratuito"] is gratuito


def test_fluxo_respeita_amostra_minima_e_aceita_nomes_sem_acento():
    r = consultar_fluxo("m boi mirim", "Santo Amaro", 7)
    assert r["viagens_amostradas"] >= 10 and r["recorte"] == "pico_manha"
