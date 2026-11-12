"""Passo 0: demanda (OD 2017) x oferta (GTFS) -> diagnóstico e redistribuição da frota.

Uso: python scripts/passo0_pipeline.py   (depois de baixar_od2017.py e baixar_dados.py)
Gera as tabelas agregadas em data/processed/ que alimentam o app e a simulação.
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from core import config as c
from core.analytics import demanda, geo, oferta
from core.frota.indicadores import indicadores, resumo
from core.frota.redistribuicao import (alvo_proporcional, maior_resto,
                                       matriz_redistribuicao, verificar)


def carregar() -> dict:
    """Lê as fontes e devolve as tabelas-base (zonas, frequências, paradas, trechos)."""
    zonas_geo = geo.zonas_od()
    gtfs = oferta.ler_gtfs()
    viagens = oferta.viagens_onibus(gtfs)
    paradas = gtfs["stops"]
    zona_parada = geo.zona_dos_pontos(paradas.stop_lon, paradas.stop_lat, zonas_geo)
    zona_parada.index = paradas.stop_id
    od = demanda.ler_od()
    return {"zonas": geo.tabela_zonas(zonas_geo), "zonas_geo": zonas_geo, "od": od, "gtfs": gtfs,
            "freq": oferta.frequencia_horaria(gtfs, viagens),
            "paradas": oferta.paradas_por_zona(gtfs, viagens, zona_parada),
            "trechos": demanda.trechos_onibus(od)}


def redistribuir_hora(h: pd.DataFrame) -> pd.DataFrame:
    """Para uma hora: frota inteira atual, alvo proporcional à carga e indicadores."""
    h = h.assign(frota_atual=maior_resto(h.frota, round(h.frota.sum())) if h.frota.sum() >= 1 else 0)
    h["necessidade"] = h.carga / (c.LOTACAO_ALVO * c.CAPACIDADE)
    h["amostra_ok"] = h.n_amostra >= c.MIN_AMOSTRA
    h["frota_alvo"] = alvo_proporcional(h.frota_atual, h.necessidade, c.PERDA_MAXIMA)
    escala = np.divide(h.frota_atual, h.frota_alvo, out=np.full(len(h), np.inf), where=h.frota_alvo > 0)
    antes = indicadores(h.frota_atual, h.carga, h.embarques, h.intervalo_min, c.CAPACIDADE)
    depois = indicadores(h.frota_alvo, h.carga, h.embarques, h.intervalo_min * escala, c.CAPACIDADE)
    return pd.concat([h.reset_index(drop=True), antes.add_suffix("_antes"), depois.add_suffix("_depois")], axis=1)


def tabela_redistribuicao(d: dict, nivel: str) -> pd.DataFrame:
    """Oferta x demanda por área e hora, com a frota-alvo e os indicadores antes/depois."""
    part = oferta.participacao(d["paradas"], d["zonas"], nivel)
    of = oferta.oferta_por_area(d["freq"], part, nivel)
    dm = demanda.demanda_por_area(d["trechos"], d["zonas"], geo.areas(d["zonas_geo"], d["zonas"], nivel), nivel)
    base = of.merge(dm, on=[nivel, "hora"], how="outer").fillna({"frota": 0, "partidas_h": 0, "embarques": 0,
                                                                 "n_amostra": 0, "carga": 0})
    return pd.concat([redistribuir_hora(h) for _, h in base.groupby("hora")], ignore_index=True)


def pressao_por_zona(d: dict) -> pd.DataFrame:
    """Embarques por lugar ofertado em cada zona e faixa do dia (só células publicáveis)."""
    partidas = oferta.partidas_por_zona(d["freq"], d["paradas"])
    z = demanda.embarques_por_zona(d["trechos"]).merge(partidas, on=["zona", "hora"], how="outer").fillna(0)
    g = z.groupby(["zona", demanda.periodo(z.hora).rename("periodo")])[["embarques", "n_amostra", "partidas_h"]].sum()
    g["pressao"] = g.embarques / (c.CAPACIDADE * g.partidas_h.where(g.partidas_h > 0))
    return g[g.n_amostra >= c.MIN_AMOSTRA].reset_index().merge(d["zonas"], on="zona")


def resumo_da_hora(t: pd.DataFrame, nivel: str, hora: int) -> dict:
    """Matriz T da hora, checagem das propriedades e indicadores da cidade antes x depois."""
    h = t[t.hora == hora]
    T = matriz_redistribuicao(h.frota_atual, h.frota_alvo)
    pd.DataFrame(T, index=h[nivel], columns=h[nivel]).to_csv(c.PROC / f"matriz_T_{nivel}_{hora:02d}h.csv")
    lado = lambda s: resumo(h.filter(like=f"_{s}").rename(columns=lambda n: n.removesuffix(f"_{s}")), h.embarques)
    return {"hora": hora, "frota_total": int(h.frota_atual.sum()),
            "onibus_realocados": int((h.frota_alvo - h.frota_atual).clip(lower=0).sum()),
            "propriedades_T": verificar(T, h.frota_atual, h.frota_alvo),
            "antes": lado("antes"), "depois": lado("depois"),
            "ocupacao_max_por_capacidade": {cap: float((h.carga / (cap * h.frota_atual)).max())
                                            for cap in c.CAPACIDADES_TESTE}}


def main():
    c.PROC.mkdir(parents=True, exist_ok=True)
    d = carregar()
    d["zonas"].to_csv(c.PROC / "zonas_sp.csv", index=False)
    pressao_por_zona(d).round(3).to_csv(c.PROC / "pressao_zona_periodo.csv", index=False)
    oferta.tabela_linhas(d["gtfs"], d["freq"], oferta.extensao_km()).to_csv(c.PROC / "linhas_onibus.csv", index=False)
    for por_periodo, nome in ((True, "periodo"), (False, "dia")):
        demanda.fluxos(d["trechos"], d["od"], d["zonas"], "subprefeitura", por_periodo).to_csv(
            c.PROC / f"fluxos_subprefeitura_{nome}.csv", index=False)
    saida = {"parametros": {"capacidade": c.CAPACIDADE, "lotacao_alvo": c.LOTACAO_ALVO,
                            "perda_maxima": c.PERDA_MAXIMA, "min_amostra": c.MIN_AMOSTRA},
             "embarques_dia": round(d["trechos"].fe.sum())}
    for nivel in ("subprefeitura", "regiao"):
        t = tabela_redistribuicao(d, nivel)
        t.round(3).to_csv(c.PROC / f"redistribuicao_{nivel}_hora.csv", index=False)
        pico = int(t.groupby("hora").carga.sum().idxmax())
        saida[nivel] = resumo_da_hora(t, nivel, pico)
    (c.PROC / "resumo_passo0.json").write_text(json.dumps(saida, indent=2, ensure_ascii=False))
    print(json.dumps(saida, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
