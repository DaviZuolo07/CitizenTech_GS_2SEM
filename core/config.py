"""Caminhos e parâmetros do produto. Parâmetro é hipótese declarada, não dado."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data/raw"
PROC = RAIZ / "data/processed"

OD_CSV = RAW / "od_sao_paulo_2017_not_harmonized.csv.gz"
GTFS_ZIP = RAW / "sptrans_gtfs.zip"

MUNI_SP = 36            # código do município de São Paulo na OD
MODO_ONIBUS = 4         # ônibus/micro/perua do município de SP
ROTA_ONIBUS = 3         # route_type do GTFS

CAPACIDADE = 80         # passageiros por ônibus (parâmetro; ver sensibilidade)
CAPACIDADES_TESTE = (60, 80, 100)
LOTACAO_ALVO = 0.85     # fração da capacidade considerada aceitável
PERDA_MAXIMA = 0.2      # fração da frota que uma área pode ceder numa hora (piso de cobertura)
MIN_AMOSTRA = 10        # células com menos viagens amostradas não são publicadas

# Faixas do dia para os fluxos (hora de saída): limites superiores inclusivos
PERIODOS = {"madrugada": 4, "pico_manha": 9, "entre_pico": 15, "pico_tarde": 19, "noite": 23}
