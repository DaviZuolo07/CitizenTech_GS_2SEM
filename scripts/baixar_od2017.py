"""Baixa os microdados da Pesquisa OD 2017 (Metrô-SP).

Portal oficial (transparencia.metrosp.com.br) em manutenção em 09/11/2026.
Fonte alternativa: espelho do pacote R `odbr` (CRAN), hospedado nas releases do GitHub hsvab/odbr.
Dado original: Companhia do Metropolitano de São Paulo — Pesquisa Origem e Destino 2017.
"""
import pathlib, urllib.request

URL = "https://github.com/hsvab/odbr/releases/latest/download/od_sao_paulo_2017_not_harmonized.csv.gz"
DEST = pathlib.Path(__file__).resolve().parents[1] / "data/raw/od_sao_paulo_2017_not_harmonized.csv.gz"

if __name__ == "__main__":
    DEST.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, DEST)
    print(f"OK -> {DEST}  (ler com pandas: sep=';')")
