"""Indicadores de atendimento por área, para comparar antes x depois."""
import numpy as np
import pandas as pd


def indicadores(frota, carga, embarques, intervalo_min, capacidade) -> pd.DataFrame:
    """Ocupação, espera, não embarcados e lugares ociosos por área.

    Hipóteses: intervalos regulares (espera = intervalo/2) e carga média ao longo
    da linha (não o trecho mais cheio). São pisos, não previsões.
    """
    frota, carga = np.asarray(frota, float), np.asarray(carga, float)
    lugares = capacidade * frota
    ocupacao = np.divide(carga, lugares, out=np.full_like(carga, np.inf), where=lugares > 0)
    excesso = np.divide(carga - lugares, carga, out=np.zeros_like(carga), where=carga > lugares)
    return pd.DataFrame({
        "ocupacao": ocupacao,
        "espera_min": np.asarray(intervalo_min, float) / 2,
        "nao_embarcados": np.asarray(embarques, float) * excesso,
        "lugares_ociosos": np.clip(lugares - carga, 0, None),
    })


def resumo(ind: pd.DataFrame, embarques) -> dict:
    """Números da cidade: espera ponderada pelos embarques e extremos de ocupação."""
    return {"espera_media_min": float(np.average(ind.espera_min, weights=embarques)),
            "ocupacao_max": float(ind.ocupacao.max()),
            "ocupacao_min": float(ind.ocupacao.min()),
            "nao_embarcados": float(ind.nao_embarcados.sum()),
            "lugares_ociosos": float(ind.lugares_ociosos.sum())}
