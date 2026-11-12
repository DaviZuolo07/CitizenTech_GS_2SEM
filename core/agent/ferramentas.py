"""Ferramentas do agente: o modelo decide quando chamar; o código decide o que devolver.

Funções puras (sem LangChain), para serem testadas sozinhas. No notebook elas são
embrulhadas com @tool. Todas devolvem um dicionário; em caso de erro, a chave
"erro" traz uma mensagem que o agente pode repassar, sem lançar exceção.
"""
import json
import pathlib
import unicodedata

import pandas as pd

from core.config import PERIODOS, PROC, RAIZ

OPERACAO = RAIZ / "base_documental/operacao_vigente.json"
DIAS = {"util": "util", "dia util": "util", "sabado": "sabado", "domingo": "domingo", "feriado": "domingo"}


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().replace("-", " ").split())


def _minutos(hhmm: str) -> int:
    h, m = str(hhmm).replace("h", ":").split(":")[:2]
    return int(h) * 60 + int(m or 0)


def _partidas(faixas: list) -> list:
    """Minutos de todas as partidas do dia. A última faixa inclui o horário final."""
    saidas = []
    for i, (inicio, fim, passo) in enumerate(faixas):
        fim_incluso = _minutos(fim) + (i == len(faixas) - 1)
        saidas += range(_minutos(inicio), fim_incluso, passo)
    return saidas


def calcular_proximo_horario(linha: str, hora: str, dia: str, caminho=OPERACAO) -> dict:
    """Próxima partida de uma linha a partir de um horário (HH:MM), em dia 'util', 'sabado', 'domingo' ou 'feriado'."""
    tabela = {k: v for k, v in json.loads(pathlib.Path(caminho).read_text(encoding="utf-8")).items() if not k.startswith("_")}
    codigo = next((k for k in tabela if _normalizar(k).startswith(_normalizar(linha))), None)
    tipo = DIAS.get(_normalizar(dia))
    if codigo is None:
        return {"erro": f"Linha '{linha}' não encontrada. Linhas disponíveis: {', '.join(tabela)}."}
    if tipo is None:
        return {"erro": f"Dia '{dia}' inválido. Use: util, sabado, domingo ou feriado."}
    try:
        agora = _minutos(hora)
    except ValueError:
        return {"erro": f"Horário '{hora}' inválido. Use o formato HH:MM."}
    saidas, base = _partidas(tabela[codigo][tipo]), {"linha": codigo, "dia": tipo, "fontes": tabela[codigo]["fontes"]}
    if not saidas:
        return {**base, "opera": False, "mensagem": f"A linha {codigo} não opera neste tipo de dia."}
    proxima = next((s for s in saidas if s >= agora), None)
    if proxima is None:
        return {**base, "opera": True, "mensagem": f"Não há mais partidas hoje. Última: {saidas[-1] // 60:02d}:{saidas[-1] % 60:02d}."}
    return {**base, "opera": True, "proxima_partida": f"{proxima // 60:02d}:{proxima % 60:02d}", "espera_min": proxima - agora}


def verificar_gratuidade(idade: int, pcd: bool, estudante: bool, dia: str) -> dict:
    """Aplica o regulamento de gratuidades (doc_04) a um perfil, em dia 'util', 'sabado', 'domingo' ou 'feriado'."""
    tipo = DIAS.get(_normalizar(dia))
    if tipo is None or not 0 <= int(idade) <= 120:
        return {"erro": "Informe idade entre 0 e 120 e dia: util, sabado, domingo ou feriado."}
    util = tipo == "util"
    regras = [
        (pcd, True, "Pessoa com deficiência: todos os dias, com Credencial de Acessibilidade válida."),
        (idade >= 65, True, "65 anos ou mais: todos os dias, com Bilhete Sênior ou documento com foto."),
        (60 <= idade <= 64, util, "De 60 a 64 anos: somente em dias úteis."),
        (idade <= 5, True, "Até 5 anos: acompanhada de responsável e sem ocupar assento."),
        (estudante, util, "Estudante: somente em dias letivos (segunda a sexta, fora de feriados e recessos), com Passe Escolar."),
    ]
    for se_aplica, gratuito, regra in regras:
        if se_aplica:
            return {"gratuito": gratuito, "regra": regra, "fonte": "doc_04"}
    return {"gratuito": False, "regra": "Demais usuários pagam a tarifa integral.", "fonte": "doc_04"}


def _periodo(hora: int) -> str:
    return next(nome for nome, limite in PERIODOS.items() if hora <= limite)


def consultar_fluxo(origem: str, destino: str, hora: int, pasta=PROC) -> dict:
    """Viagens de ônibus por dia entre duas subprefeituras (OD 2017), na faixa do dia da hora informada."""
    if not 0 <= int(hora) <= 23:
        return {"erro": "Hora inválida. Use um número de 0 a 23."}
    por_faixa, por_dia = (pd.read_csv(f"{pasta}/fluxos_subprefeitura_{n}.csv") for n in ("periodo", "dia"))
    nomes = {_normalizar(n): n for n in pd.concat([por_dia.origem, por_dia.destino]).unique()}
    par = [nomes.get(_normalizar(x)) for x in (origem, destino)]
    if None in par:
        return {"erro": f"Subprefeitura não encontrada. Disponíveis: {', '.join(sorted(nomes.values()))}."}
    base = {"origem": par[0], "destino": par[1], "fonte": "Pesquisa OD 2017 (Metrô-SP), dado agregado"}
    for tabela, recorte in ((por_faixa[por_faixa.periodo == _periodo(int(hora))], _periodo(int(hora))), (por_dia, "dia inteiro")):
        achado = tabela[(tabela.origem == par[0]) & (tabela.destino == par[1])]
        if len(achado):
            return {**base, "recorte": recorte, "viagens_por_dia": int(achado.viagens.iloc[0]), "viagens_amostradas": int(achado.n_amostra.iloc[0])}
    return {**base, "erro": "Sem dado publicável para este par: menos de 10 viagens na amostra da pesquisa."}
