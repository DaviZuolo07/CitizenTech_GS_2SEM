"""Coletor da API Olho Vivo (SPTrans): grava a posição de todos os ônibus a cada 30 s.

Uso:
    crie o arquivo .env na raiz do repositório com:  OLHOVIVO_TOKEN=seu_token
    python scripts/coletor_olhovivo.py    (Ctrl+C para parar)

Grava a resposta bruta, comprimida, em data/olhovivo/AAAA-MM-DD/posicao_HHMMSS.json.gz.
A interpretação dos campos fica para a análise: assim nenhum dado se perde por erro de parsing.
O token só é lido da variável de ambiente; nunca é gravado em arquivo nem impresso.
"""
import datetime as dt
import gzip
import json
import os
import pathlib
import sys
import time

import requests

BASE = "http://api.olhovivo.sptrans.com.br/v2.1"
INTERVALO_S = 30
DESTINO = pathlib.Path(__file__).resolve().parents[1] / "data" / "olhovivo"


def autenticar(sessao: requests.Session, token: str) -> None:
    r = sessao.post(f"{BASE}/Login/Autenticar", params={"token": token}, timeout=20)
    if r.status_code != 200 or r.text.strip().lower() != "true":
        sys.exit(f"autenticação recusada (HTTP {r.status_code}, resposta {r.text[:40]!r}): confira o token")


def contar_veiculos(dados) -> int:
    """Conta veículos sem depender do nome exato dos campos (lista 'l' de linhas, cada uma com 'vs')."""
    linhas = dados.get("l", []) if isinstance(dados, dict) else []
    return sum(len(linha.get("vs", [])) for linha in linhas if isinstance(linha, dict))


def main() -> None:
    token = os.environ.get("OLHOVIVO_TOKEN")
    env = pathlib.Path(__file__).resolve().parents[1] / ".env"
    if not token and env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            chave, _, valor = linha.partition("=")
            if chave.strip() == "OLHOVIVO_TOKEN":
                token = valor.strip().strip('"')
    if not token:
        sys.exit("token não encontrado: crie o arquivo .env com OLHOVIVO_TOKEN=... na raiz do repositório")
    sessao = requests.Session()
    autenticar(sessao, token)
    print(f"autenticado; gravando em {DESTINO} a cada {INTERVALO_S} s (Ctrl+C para parar)")
    falhas = 0
    while True:
        inicio = time.time()
        agora = dt.datetime.now()
        try:
            r = sessao.get(f"{BASE}/Posicao", timeout=25)
            if r.status_code == 401:                      # sessão expirou: autentica de novo
                autenticar(sessao, token)
                r = sessao.get(f"{BASE}/Posicao", timeout=25)
            r.raise_for_status()
            dados = r.json()
            if dados is None:                             # a API às vezes responde null; não grava arquivo vazio
                raise ValueError("resposta vazia")
            pasta = DESTINO / agora.strftime("%Y-%m-%d")
            pasta.mkdir(parents=True, exist_ok=True)
            with gzip.open(pasta / f"posicao_{agora:%H%M%S}.json.gz", "wt", encoding="utf-8") as f:
                json.dump({"coletado_em": agora.isoformat(timespec="seconds"), "resposta": dados}, f)
            falhas = 0
            print(f"{agora:%H:%M:%S}  {contar_veiculos(dados):>6} veículos")
        except (requests.RequestException, ValueError) as erro:
            falhas += 1
            print(f"{agora:%H:%M:%S}  falha {falhas}: {type(erro).__name__}; tento de novo no próximo ciclo")
            if falhas >= 10:                              # API fora do ar (já aconteceu em abr e set/2026)
                time.sleep(120)
        time.sleep(max(0.0, INTERVALO_S - (time.time() - inicio)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ncoleta encerrada")
