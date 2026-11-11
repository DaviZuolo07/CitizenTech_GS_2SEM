"""Demanda: da Pesquisa OD 2017 a embarques, carga a bordo e fluxos de ônibus.

A unidade é o TRECHO de ônibus, não a viagem: quem pega ônibus até o metrô tem
modo principal "metrô", mas embarcou num ônibus. Tudo sai agregado (LGPD).
"""
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from core.config import MIN_AMOSTRA, MODO_ONIBUS, OD_CSV, PERIODOS

PONTOS = ("o", "t1", "t2", "t3", "d")   # origem, até 3 transferências, destino
COLUNAS = (["id_ordem", "fe_via", "h_saida", "duracao", "anda_o", "anda_d", "modoprin"]
           + [f"modo{i}" for i in range(1, 5)]
           + [c.format(p) for p in PONTOS for c in ("zona_{}", "co_{}_x", "co_{}_y")])


def ler_od(caminho=OD_CSV) -> pd.DataFrame:
    """Registros da OD que são viagens (pessoas sem viagem têm modo1 vazio)."""
    od = pd.read_csv(caminho, sep=";", usecols=COLUNAS)
    return od[od.modo1.notna()]


def _trecho(od: pd.DataFrame, i: int) -> pd.DataFrame:
    """Trecho i da viagem: do ponto i-1 até a próxima transferência (ou o destino)."""
    ini = PONTOS[i - 1]
    ultimo = od[f"modo{i + 1}"].isna() if i < 4 else pd.Series(True, index=od.index)
    fim = lambda col: od[col.format("d")].where(ultimo, od[col.format(PONTOS[i])])
    t = pd.DataFrame({"viagem": od.id_ordem, "modo": od[f"modo{i}"],
                      "zona_emb": od[f"zona_{ini}"], "zona_des": fim("zona_{}"),
                      "x_emb": od[f"co_{ini}_x"], "y_emb": od[f"co_{ini}_y"],
                      "x_des": fim("co_{}_x"), "y_des": fim("co_{}_y")})
    return t.assign(dist=np.hypot(t.x_des - t.x_emb, t.y_des - t.y_emb))


def trechos_onibus(od: pd.DataFrame) -> pd.DataFrame:
    """Um registro por trecho de ônibus municipal, com o tempo a bordo estimado.

    O tempo em veículo da viagem (duração menos caminhadas) é repartido entre os
    trechos na proporção da distância em linha reta. Inclui espera: é teto.
    """
    t = pd.concat([_trecho(od, i) for i in range(1, 5)]).dropna(subset="modo")
    por_viagem = t.groupby("viagem").dist
    fracao = (t.dist / por_viagem.transform("sum")).fillna(1 / por_viagem.transform("size"))
    v = od.set_index("id_ordem")
    em_veiculo = (v.duracao - v.anda_o.fillna(0) - v.anda_d.fillna(0)).clip(lower=1)
    t = t.assign(min_bordo=fracao * t.viagem.map(em_veiculo), fe=t.viagem.map(v.fe_via),
                 hora=t.viagem.map(v.h_saida).astype(int))
    return t[t.modo == MODO_ONIBUS].drop(columns="modo")


def embarques_por_zona(trechos: pd.DataFrame) -> pd.DataFrame:
    """Embarques expandidos e viagens amostradas por zona de embarque e hora."""
    g = trechos.groupby(["zona_emb", "hora"]).fe.agg(embarques="sum", n_amostra="size")
    return g.reset_index().rename(columns={"zona_emb": "zona"})


def carga_por_area(trechos: pd.DataFrame, areas: gpd.GeoDataFrame, nivel: str) -> pd.Series:
    """Passageiros a bordo (média na hora) por área e hora.

    A carga de cada trecho (fe x horas a bordo) é repartida pelas áreas que a
    reta embarque -> desembarque atravessa, na proporção do comprimento. É o
    mesmo critério da frota, repartida pelas paradas ao longo da linha.
    """
    t = trechos.reset_index(drop=True)
    fim = t[["x_des", "y_des"]].to_numpy() + (t.dist.to_numpy() == 0)[:, None]   # 1 m se parado
    retas = shapely.linestrings(np.stack([t[["x_emb", "y_emb"]].to_numpy(), fim], axis=1))
    cortes = gpd.overlay(gpd.GeoDataFrame({"i": t.index}, geometry=retas, crs=areas.crs), areas)
    fracao = cortes.length / cortes.length.groupby(cortes.i).transform("sum")
    peso = fracao * cortes.i.map(t.fe * t.min_bordo / 60)
    return peso.groupby([cortes[nivel], cortes.i.map(t.hora).rename("hora")]).sum().rename("carga")


def demanda_por_area(trechos: pd.DataFrame, zonas: pd.DataFrame, areas: gpd.GeoDataFrame,
                     nivel: str) -> pd.DataFrame:
    """Embarques/h (na área de embarque) e carga a bordo por área e hora."""
    emb = trechos.assign(**{nivel: trechos.zona_emb.map(zonas.set_index("zona")[nivel])})
    embarques = emb.groupby([nivel, "hora"]).fe.agg(embarques="sum", n_amostra="size")
    return embarques.join(carga_por_area(trechos, areas, nivel), how="outer").fillna(0).reset_index()


def periodo(hora: pd.Series) -> pd.Series:
    """Faixa do dia (madrugada, pico_manha, ...) de cada hora de saída."""
    return pd.cut(hora, [-1, *PERIODOS.values()], labels=list(PERIODOS)).astype(str)


def fluxos(trechos: pd.DataFrame, od: pd.DataFrame, zonas: pd.DataFrame, nivel: str,
           por_periodo=True) -> pd.DataFrame:
    """Viagens que usam ônibus entre áreas de origem e destino (por faixa do dia ou no dia).

    Só publica células com pelo menos MIN_AMOSTRA viagens amostradas: abaixo disso
    o número é ruído estatístico e se aproxima de identificar pessoas.
    """
    area = zonas.set_index("zona")[nivel]
    v = od[od.id_ordem.isin(trechos.viagem)]
    chaves = [v.zona_o.map(area).rename("origem"), v.zona_d.map(area).rename("destino")]
    chaves += [periodo(v.h_saida).rename("periodo")] if por_periodo else []
    g = v.groupby(chaves).fe_via.agg(viagens="sum", n_amostra="size").reset_index()
    return g[g.n_amostra >= MIN_AMOSTRA].round({"viagens": 0})
