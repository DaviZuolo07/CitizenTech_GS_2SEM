"""Baixa os dados complementares do produto (oferta e geografia) para data/raw/.

Todos os arquivos vêm de endereços públicos e fixos (commit ou release travados),
para que o pipeline seja reproduzível. Fontes originais:
- GTFS: SPTrans (sptrans.com.br/desenvolvedores). Aqui usamos uma cópia pública
  no GitHub porque o portal exige login. Para trocar pelo arquivo oficial, basta
  salvar o .zip em data/raw/sptrans_gtfs.zip.
- Zonas e distritos da OD 2017: Metrô-SP, via espelho do pacote R `odbr`.
- Distritos e subprefeituras: GeoSampa (Prefeitura de São Paulo).
"""
import pathlib
import urllib.request

RAW = pathlib.Path(__file__).resolve().parents[1] / "data/raw"
ODBR = "https://github.com/hsvab/odbr/releases/download/v0.1.0/"
MIRROR = ("https://raw.githubusercontent.com/Mindful-AI-Research/"
          "4-project-ai-ml-geospatial-transit-desert-mapper/")
ARQUIVOS = {
    "od_zonas_2017.gpkg": ODBR + "zone_sao_paulo_2017_not_harmonized.gpkg",
    "od_distritos_2017.gpkg": ODBR + "district_sao_paulo_2017_not_harmonized.gpkg",
    "sptrans_gtfs.zip": MIRROR + "725fa86c9c28df06adfb287958b929510ffac6ef/data/raw/SPTrans/sptrans_gtfs.zip",
    "geosampa_distritos.gpkg": MIRROR + "eb51f7b0c5235635cf9207069b54273347ae642f/data/raw/geosampa/distrito_municipal_v2.gpkg",
    "geosampa_subprefeituras.gpkg": MIRROR + "eb51f7b0c5235635cf9207069b54273347ae642f/data/raw/geosampa/subprefeitura_v2.gpkg",
}

if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    for nome, url in ARQUIVOS.items():
        destino = RAW / nome
        if destino.exists():
            print(f"já existe  {nome}")
            continue
        urllib.request.urlretrieve(url, destino)
        print(f"baixado    {nome}  ({destino.stat().st_size / 1e6:.1f} MB)")
