"""Servidor local do Linha Certa: ponte entre o navegador e a API Olho Vivo da SPTrans.

Por que um servidor no meio: a API autentica por cookie de sessão e não libera chamadas diretas do navegador
(CORS); e o token não pode ir para o navegador, onde qualquer um o leria.

Uso, na raiz do repositório:
    1. crie o arquivo .env com uma linha:  OLHOVIVO_TOKEN=seu_token   (o .env não vai para o git)
    2. python app/servidor.py
    3. abra http://localhost:8000
"""
import http.server
import json
import os
import pathlib
import threading
import time
import urllib.parse

import requests

import cidadao
import painel
import simulacao

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
BASE = os.environ.get("OLHOVIVO_BASE", "http://api.olhovivo.sptrans.com.br/v2.1")
PORTA = int(os.environ.get("PORTA", "8000"))
CACHE_S = 15          # a API atualiza as posições a cada ~30 s; mais que isso só gasta requisição


def ler_token() -> str:
    token = os.environ.get("OLHOVIVO_TOKEN")
    env = RAIZ / ".env"
    if not token and env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            chave, _, valor = linha.partition("=")
            if chave.strip() == "OLHOVIVO_TOKEN":
                token = valor.strip().strip('"')
    if not token:
        raise SystemExit("token não encontrado: crie o arquivo .env com OLHOVIVO_TOKEN=... na raiz do repositório")
    return token


class OlhoVivo:
    def __init__(self, token: str):
        self.token, self.sessao, self.trava = token, requests.Session(), threading.Lock()
        self.cache, self.quando = {}, {}
        self.autenticar()

    def autenticar(self) -> None:
        r = self.sessao.post(f"{BASE}/Login/Autenticar", params={"token": self.token}, timeout=20)
        if r.status_code != 200 or r.text.strip().lower() != "true":
            raise SystemExit(f"autenticação recusada pela API (HTTP {r.status_code}): confira o token")

    def consultar(self, caminho: str, **params):
        """GET com cache curto e nova autenticação se a sessão expirar."""
        chave = caminho + json.dumps(params, sort_keys=True)
        with self.trava:
            if chave in self.cache and time.time() - self.quando[chave] < CACHE_S:
                return self.cache[chave]
            r = self.sessao.get(f"{BASE}{caminho}", params=params, timeout=25)
            if r.status_code == 401:
                self.autenticar()
                r = self.sessao.get(f"{BASE}{caminho}", params=params, timeout=25)
            r.raise_for_status()
            dados = r.json()
            if dados is None:                     # a API às vezes responde null (logo após autenticar ou sob carga)
                raise requests.RequestException("a API respondeu vazio")
            self.cache[chave], self.quando[chave] = dados, time.time()
            return dados


MAPA_EMPRESAS = RAIZ / "data" / "processed" / "prefixo_empresa.json"


def mapa_empresas() -> dict:
    """Grupo de prefixo (2 primeiros dígitos) -> empresa. Gerado e completado por scripts/empresas_linhas.py."""
    try:
        return json.loads(MAPA_EMPRESAS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def achatar_posicoes(dados: dict) -> dict:
    """Resposta de /Posicao (linhas com veículos) vira uma lista plana de veículos, com a empresa de cada um."""
    mapa = mapa_empresas()
    veiculos = []
    for l in dados.get("l", []):
        for v in l.get("vs", []):
            g = str(v.get("p"))[:2]
            veiculos.append({"linha": l.get("c"), "codigo_linha": l.get("cl"), "sentido": l.get("sl"),
                             "letreiros": [l.get("lt0"), l.get("lt1")], "prefixo": v.get("p"), "acessivel": v.get("a"),
                             "lat": v.get("py"), "lon": v.get("px"), "atualizado": v.get("ta"),
                             "empresa": mapa.get(g, {}).get("empresa", f"não identificada (área {g[:1]})")})
    return {"hora": dados.get("hr"), "total": len(veiculos), "veiculos": veiculos}


class Rotas(http.server.SimpleHTTPRequestHandler):
    api: OlhoVivo = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(AQUI / "web"), **kwargs)

    def responder_json(self, corpo, status=200):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        try:
            if url.path == "/api/regularidade":
                return self.responder_json(painel.regularidade())
            if url.path == "/api/realocacao":       # /api/realocacao?lote=D01&perda=0.2&hmax=15
                return self.responder_json(painel.realocacao(q.get("lote", ""), q.get("perda", painel.PERDA_MAXIMA),
                                                             q.get("hmax", painel.LIMITE_EWT)))
            if url.path == "/api/cidadao/fontes":
                return self.responder_json(cidadao.fontes())
            if url.path == "/api/simulacao/lista":   # F4: simulações preparadas por scripts/simulacao_preparar.py
                return self.responder_json(simulacao.lista())
            if url.path == "/api/simulacao":         # /api/simulacao?arquivo=sim_<dia>_<lote>_<janela>.json
                return self.responder_json(simulacao.carregar(q.get("arquivo", "")))
            if url.path.startswith("/api/") and self.api is None:
                return self.responder_json({"erro": "sem conexão com a API Olho Vivo (modo offline)"}, 503)
            if url.path == "/api/posicao":
                return self.responder_json(achatar_posicoes(self.api.consultar("/Posicao")))
            if url.path == "/api/empresas":
                return self.responder_json(self.api.consultar("/Empresa"))
            if url.path == "/api/linhas":            # busca por número ou nome: /api/linhas?termo=8000
                return self.responder_json(self.api.consultar("/Linha/Buscar", termosBusca=q.get("termo", "")))
            if url.path == "/api/previsao":          # chegada prevista numa parada: /api/previsao?parada=...
                return self.responder_json(self.api.consultar("/Previsao/Parada", codigoParada=q.get("parada", "")))
        except requests.RequestException as erro:
            return self.responder_json({"erro": f"API Olho Vivo indisponível: {type(erro).__name__}"}, 502)
        except (OSError, ValueError, KeyError) as erro:   # saída do motor ausente ou parâmetro inválido
            return self.responder_json({"erro": f"{type(erro).__name__}: {erro}"}, 500)
        return super().do_GET()

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/api/cidadao":
            return self.responder_json({"erro": "rota inexistente"}, 404)
        try:
            tamanho = min(int(self.headers.get("Content-Length", 0)), 4000)
            pergunta = json.loads(self.rfile.read(tamanho) or b"{}").get("pergunta", "")
            return self.responder_json(cidadao.responder(pergunta))
        except (ValueError, AttributeError):
            return self.responder_json({"erro": "envie JSON no formato {\"pergunta\": \"...\"}"}, 400)
        except RuntimeError as erro:                 # nenhum provedor de LLM respondeu (sem chave, cota, rede)
            return self.responder_json({"erro": str(erro)}, 503)

    def log_message(self, *args):               # silencia o log por requisição
        pass


if __name__ == "__main__":
    try:                                            # sem token ou sem API, as abas do motor e do cidadão seguem no ar
        Rotas.api = OlhoVivo(ler_token())
        print("conectado à API Olho Vivo")
    except (SystemExit, requests.RequestException) as erro:
        print(f"modo offline (mapa ao vivo desligado): {erro}")
    print(f"abra http://localhost:{PORTA}  (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORTA), Rotas).serve_forever()
