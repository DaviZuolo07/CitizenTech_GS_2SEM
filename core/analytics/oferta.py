"""Oferta: do GTFS da SPTrans à frota em operação por região e hora.

O GTFS não informa quantos ônibus cada linha usa. Reconstruímos pela relação
veículos em operação = tempo de viagem x frequência (Lei de Little), por sentido.
"""
import zipfile

import pandas as pd

from core.config import GTFS_ZIP, ROTA_ONIBUS

TABELAS = ("routes", "trips", "frequencies", "stop_times", "stops", "calendar")


def ler_gtfs(caminho=GTFS_ZIP) -> dict:
    """Tabelas do feed como DataFrames, sem linhas duplicadas."""
    with zipfile.ZipFile(caminho) as z:
        return {t: pd.read_csv(z.open(f"{t}.txt")).drop_duplicates() for t in TABELAS}


def viagens_onibus(gtfs: dict) -> pd.DataFrame:
    """Viagens-modelo de ônibus em dia útil, com a duração em minutos (índice: trip_id)."""
    util = gtfs["calendar"].query("monday == 1").service_id
    rotas = gtfs["routes"].query("route_type == @ROTA_ONIBUS").route_id
    v = gtfs["trips"].query("route_id in @rotas and service_id in @util").set_index("trip_id")
    t = gtfs["stop_times"]
    seg = pd.to_timedelta(t.arrival_time).dt.total_seconds()
    dur = seg.groupby(t.trip_id).agg(lambda s: s.max() - s.min()) / 60
    return v.assign(dur_min=dur)[["route_id", "direction_id", "dur_min"]]


def frequencia_horaria(gtfs: dict, viagens: pd.DataFrame) -> pd.DataFrame:
    """Por viagem e hora: partidas/h, intervalo (min) e frota em operação."""
    f = gtfs["frequencies"].merge(viagens[["dur_min"]], left_on="trip_id", right_index=True)
    f["hora"] = f.start_time.str[:2].astype(int)
    f["partidas_h"] = 3600 / f.headway_secs
    f["intervalo_min"] = f.headway_secs / 60
    f["frota"] = f.partidas_h * f.dur_min / 60
    return f[["trip_id", "hora", "partidas_h", "intervalo_min", "frota"]]


def paradas_por_zona(gtfs: dict, viagens: pd.DataFrame, zona_da_parada: pd.Series) -> pd.DataFrame:
    """Número de paradas de cada viagem em cada zona do município (trip_id, zona, paradas)."""
    st = gtfs["stop_times"].query("trip_id in @viagens.index")
    st = st.assign(zona=st.stop_id.map(zona_da_parada)).dropna(subset="zona")
    return st.groupby(["trip_id", "zona"]).size().rename("paradas").reset_index()


def participacao(paradas: pd.DataFrame, zonas: pd.DataFrame, nivel: str) -> pd.DataFrame:
    """Fração s(viagem, área) das paradas de cada viagem em cada área. Soma 1 por viagem."""
    p = paradas.merge(zonas[["zona", nivel]]).groupby(["trip_id", nivel]).paradas.sum()
    return (p / p.groupby("trip_id").transform("sum")).rename("s").reset_index()


def oferta_por_area(freq: pd.DataFrame, part: pd.DataFrame, nivel: str) -> pd.DataFrame:
    """Frota, partidas/h e intervalo médio por área e hora. Preserva a frota total (x = S n)."""
    m = freq.merge(part, on="trip_id")
    m = m.assign(frota=m.frota * m.s, partidas_h=m.partidas_h * m.s, hs=m.intervalo_min * m.s)
    g = m.groupby([nivel, "hora"])[["frota", "partidas_h", "hs", "s"]].sum()
    return g.assign(intervalo_min=g.hs / g.s)[["frota", "partidas_h", "intervalo_min"]].reset_index()


def partidas_por_zona(freq: pd.DataFrame, paradas: pd.DataFrame) -> pd.DataFrame:
    """Partidas/h de todas as viagens que param na zona, por zona e hora."""
    m = freq.merge(paradas[["trip_id", "zona"]], on="trip_id")
    return m.groupby(["zona", "hora"]).partidas_h.sum().reset_index()


def extensao_km(caminho=GTFS_ZIP) -> pd.Series:
    """Extensão de cada trajeto (shape_id) em km, lida do shapes.txt."""
    with zipfile.ZipFile(caminho) as z:
        sh = pd.read_csv(z.open("shapes.txt"), usecols=["shape_id", "shape_dist_traveled"])
    return sh.groupby("shape_id").shape_dist_traveled.max() / 1000


def tabela_linhas(gtfs: dict, freq: pd.DataFrame, km: pd.Series) -> pd.DataFrame:
    """Uma linha por sentido de cada linha de ônibus: de onde até onde, extensão, partidas e frota estimada."""
    v = gtfs["trips"].merge(gtfs["routes"][["route_id", "route_long_name"]], on="route_id").set_index("trip_id")
    por_hora = freq.pivot_table(index="trip_id", columns="hora", values="frota", aggfunc="sum").reindex(columns=range(24), fill_value=0).fillna(0)
    t = pd.DataFrame({"linha": v.route_id, "sentido": v.direction_id, "trajeto": v.route_long_name, "destino": v.trip_headsign,
                      "extensao_km": v.shape_id.map(km), "partidas_dia": freq.groupby("trip_id").partidas_h.sum(),
                      "frota_6h": por_hora[6], "frota_17h": por_hora[17], "frota_max": por_hora.max(axis=1)})
    return t.dropna(subset="partidas_dia").round(1).sort_values("frota_max", ascending=False).reset_index(names="viagem")
