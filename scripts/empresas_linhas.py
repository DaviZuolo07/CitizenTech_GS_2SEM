"""Separa a frota de São Paulo por empresa, com a API Olho Vivo.

Regra descoberta nos dados (19/11/2026): os dois primeiros dígitos do prefixo do ônibus identificam a empresa
(o 1º é a área de operação, 1 a 8; o 2º, a empresa dentro da área). Conferido em 35 grupos, nenhum misturando
empresas.

Passos:
  1. /Empresa: empresas e áreas.
  2. /Posicao/Garagem?codigoEmpresa=X: ônibus na garagem de cada empresa -> grupo de prefixo -> empresa.
     O mapa é acumulado em data/processed/prefixo_empresa.json: cada execução completa os grupos que faltam.
  3. /Posicao: toda a frota na rua; cada linha-sentido recebe a empresa da maioria dos seus ônibus.
Saídas em data/processed/: linha_empresa.csv, empresas.csv, prefixo_empresa.json
Uso: python scripts/empresas_linhas.py   (token no .env, nunca impresso)
"""
import collections
import csv
import datetime as dt
import json
import pathlib
import sys

import requests

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BASE = "http://api.olhovivo.sptrans.com.br/v2.1"
SAIDA = RAIZ / "data" / "processed"
MAPA = SAIDA / "prefixo_empresa.json"
grupo = lambda prefixo: str(prefixo)[:2]


def sessao() -> requests.Session:
    tok = next((v.strip().strip('"') for k, _, v in (l.partition("=") for l in (RAIZ / ".env").read_text(encoding="utf-8").splitlines())
                if k.strip() == "OLHOVIVO_TOKEN"), None)
    if not tok:
        sys.exit("OLHOVIVO_TOKEN não encontrado no .env")
    s = requests.Session()
    if s.post(f"{BASE}/Login/Autenticar", params={"token": tok}, timeout=20).text.strip().lower() != "true":
        sys.exit("autenticação recusada")
    return s


def atualizar_mapa(s: requests.Session) -> dict:
    mapa = json.loads(MAPA.read_text(encoding="utf-8")) if MAPA.exists() else {}
    empresas = {}
    for area in s.get(f"{BASE}/Empresa", timeout=30).json()["e"]:
        for e in area["e"]:
            empresas.setdefault(e["c"], e["n"])
    for codigo, nome in empresas.items():
        dados = s.get(f"{BASE}/Posicao/Garagem", params={"codigoEmpresa": codigo}, timeout=30).json() or {}
        for l in dados.get("l", []):
            for v in l.get("vs", []):
                g = grupo(v["p"])
                anterior = mapa.get(g)
                if anterior and anterior["empresa_codigo"] != codigo:
                    print(f"AVISO: grupo {g} visto em {anterior['empresa']} e em {nome}; mantido o primeiro")
                    continue
                mapa[g] = {"empresa_codigo": codigo, "empresa": nome, "area": int(g[0])}
    MAPA.write_text(json.dumps(dict(sorted(mapa.items())), ensure_ascii=False, indent=1), encoding="utf-8")
    return mapa


def main() -> None:
    s = sessao()
    mapa = atualizar_mapa(s)
    pos = s.get(f"{BASE}/Posicao", timeout=30).json() or {}
    agora = dt.datetime.now().isoformat(timespec="minutes")
    linhas, sem_mapa = [], collections.Counter()
    for l in pos.get("l", []):
        grupos = collections.Counter(grupo(v["p"]) for v in l.get("vs", []))
        conhecidos = collections.Counter({g: n for g, n in grupos.items() if g in mapa})
        sem_mapa.update({g: n for g, n in grupos.items() if g not in mapa})
        g, n = conhecidos.most_common(1)[0] if conhecidos else (None, 0)
        linhas.append({"linha": l["c"], "codigo_linha": l["cl"], "sentido": l["sl"],
                       "letreiro_0": l.get("lt0"), "letreiro_1": l.get("lt1"),
                       "empresa_codigo": mapa[g]["empresa_codigo"] if g else "", "empresa": mapa[g]["empresa"] if g else "",
                       "area": mapa[g]["area"] if g else (int(next(iter(grupos))[0]) if grupos else ""),
                       "onibus_agora": sum(grupos.values()),
                       "fracao_da_empresa": round(n / sum(grupos.values()), 3) if grupos else 0,
                       "consultado_em": agora})
    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "linha_empresa.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)

    resumo = collections.defaultdict(lambda: {"linhas": set(), "onibus_agora": 0})
    for r in linhas:
        chave = (r["empresa_codigo"], r["empresa"] or "NÃO IDENTIFICADA", r["area"] if not r["empresa"] else "")
        resumo[chave]["linhas"].add(r["linha"]); resumo[chave]["onibus_agora"] += r["onibus_agora"]
    with open(SAIDA / "empresas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["empresa_codigo", "empresa", "area_se_nao_identificada", "linhas", "onibus_agora"])
        for (c, e, a), v in sorted(resumo.items(), key=lambda kv: -kv[1]["onibus_agora"]):
            w.writerow([c, e, a, len(v["linhas"]), v["onibus_agora"]])

    total = sum(r["onibus_agora"] for r in linhas)
    ident = sum(r["onibus_agora"] for r in linhas if r["empresa"])
    print(f"{agora}: {total} ônibus na rua em {len({r['linha'] for r in linhas})} linhas; "
          f"{ident} ({ident / max(total, 1):.0%}) com empresa identificada; {len(mapa)} grupos de prefixo no mapa")
    if sem_mapa:
        print("grupos ainda sem empresa (rode de novo mais tarde, quando esses ônibus passarem pela garagem):",
              dict(sem_mapa.most_common()))


if __name__ == "__main__":
    main()
