"""Geografia: zona OD -> distrito -> subprefeitura -> região (GeoSampa)."""
import geopandas as gpd
import pandas as pd

from core.config import MUNI_SP, RAW


def zonas_od() -> gpd.GeoDataFrame:
    """Polígonos das 517 zonas da OD 2017, com o número da zona e o município."""
    z = gpd.read_file(RAW / "od_zonas_2017.gpkg")
    z = z.rename(columns={"NumeroZona": "zona", "NomeZona": "nome_zona", "NumeroMuni": "muni"})
    z = z.set_geometry(z.buffer(0))   # corrige polígonos inválidos do arquivo original
    return z[["zona", "nome_zona", "muni", "geometry"]].astype({"zona": int, "muni": int})


def distritos() -> gpd.GeoDataFrame:
    """Distritos do município com a subprefeitura e a região a que pertencem."""
    chave = "cd_identificador_subprefeitura"
    nomes = {"nm_distrito_municipal": "distrito", "nm_subprefeitura": "subprefeitura",
             "nm_regiao_05": "regiao"}
    sub = gpd.read_file(RAW / "geosampa_subprefeituras.gpkg", columns=[chave, "nm_subprefeitura"])
    d = gpd.read_file(RAW / "geosampa_distritos.gpkg", columns=[chave, *nomes]).merge(
        sub.drop(columns="geometry"), on=chave)
    return d.rename(columns=nomes)[[*nomes.values(), "geometry"]]


def tabela_zonas(zonas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Uma linha por zona do município: zona, distrito, subprefeitura, região.

    Cada zona OD fica dentro de um distrito, então um ponto interno da zona basta.
    """
    sp = zonas[zonas.muni == MUNI_SP]
    d = distritos()
    pontos = sp.set_geometry(sp.representative_point()).to_crs(d.crs)
    t = gpd.sjoin(pontos, d, predicate="within")
    return pd.DataFrame(t[["zona", "nome_zona", "distrito", "subprefeitura", "regiao"]])


def zona_dos_pontos(lon, lat, zonas: gpd.GeoDataFrame) -> pd.Series:
    """Zona OD que contém cada ponto (lon/lat em WGS84). NaN se cair fora."""
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(lon, lat), crs=4326).to_crs(zonas.crs)
    j = gpd.sjoin(pts, zonas[["zona", "geometry"]], predicate="within", how="left")
    return j[~j.index.duplicated()].zona


def areas(zonas: gpd.GeoDataFrame, tabela: pd.DataFrame, nivel: str) -> gpd.GeoDataFrame:
    """Polígonos do nível pedido (distrito, subprefeitura ou região), unindo as zonas."""
    return zonas.merge(tabela[["zona", nivel]]).dissolve(nivel).reset_index()[[nivel, "geometry"]]
