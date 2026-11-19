"""Simulação do dia real (F4): serve ao navegador os arquivos gravados por scripts/simulacao_preparar.py.

O cálculo pesado (projeção das posições no traçado, esperas pelo motor) roda no preparo; aqui só se lê JSON,
para o app subir no Python do Windows sem scipy. Rotas (em servidor.py):
    /api/simulacao/lista            arquivos disponíveis, com lote, janela e resumo
    /api/simulacao?arquivo=<nome>   um arquivo inteiro (replay, traçados, linhas, esperas, hipóteses)
"""
import json
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1] / "data" / "processed" / "simulacao"
_cache = {}


def _ler(p: Path) -> dict:
    t = p.stat().st_mtime
    if _cache.get(p.name, (None,))[0] != t:
        _cache[p.name] = (t, json.loads(p.read_text(encoding="utf-8")))
    return _cache[p.name][1]


def lista() -> dict:
    """Mais recente primeiro (dia e janela); no mesmo horário, o lote que mais poupa no M2. Sem as posições."""
    itens = []
    for p in sorted(PASTA.glob("sim_*.json"), reverse=True):
        try:
            s = _ler(p)
        except (OSError, ValueError):          # arquivo sendo gravado pelo preparo
            continue
        itens.append({"arquivo": p.name, "lote": s["lote"], "empresa": s["empresa"], "dia": s["dia"],
                      "janela": s["janela"], "gerado_em": s["gerado_em"], "resumo": s["resumo"]})
    itens.sort(key=lambda i: (i["dia"], i["janela"][0], i["resumo"].get("horas_poupadas_dia_motor") or 0), reverse=True)
    return {"arquivos": itens}


def carregar(arquivo: str) -> dict:
    """Só nomes que estão na pasta (nada de caminho vindo do navegador)."""
    nomes = {p.name: p for p in PASTA.glob("sim_*.json")}
    if arquivo not in nomes:
        raise KeyError(f"simulação inexistente: {arquivo}")
    return _ler(nomes[arquivo])
