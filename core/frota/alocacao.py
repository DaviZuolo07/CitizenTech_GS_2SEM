"""F2 — Frota por linha dentro de cada lote (M2 do caderno), com a mesma frota.

Espera média na linha l com frota n_l e ciclo t_l (ônibus regulares): t_l / (2 n_l).
Objetivo: minimizar Σ d_l · t_l / n_l^m  com  Σ n_l = B (frota do lote)  e  n_l >= ceil((1 - perda_max) · n_l atual).
m = 1 é a espera total (regra da raiz, n ∝ √(d·t)); em geral o ótimo é n ∝ (d·t)^k com k = 1/(1+m)
(k = 2/3 ⇒ m = 1/2, cenário de lotação). Ônibus inteiros por alocação gulosa do maior ganho marginal,
ótima porque o objetivo é separável e convexo.
"""
import heapq

import numpy as np
import pandas as pd


def demanda_planilha(caminho, dias: int) -> pd.DataFrame:
    """Passageiros/dia, lote e empresa de cada linha (planilha mensal da SPTrans); código no formato do Olho Vivo."""
    df = pd.read_excel(caminho, header=3)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["Linha"])
    cod = df.Linha.astype(str).str.split(" - ").str[0].str.strip()
    df = df[cod.str.len() == 6].assign(c=cod.str[:4] + "-" + cod.str[4:6], lote=df.Lote.str.strip(),
                                       empresa_lote=df.Empresa.str.split().str[1:].str.join(" "),
                                       passageiros_dia=df["Tot Passageiros Transportados"] / dias)
    # linha listada em mais de um lote (resíduo de transferência): fica o lote com mais passageiros
    df = df.sort_values("passageiros_dia").drop_duplicates("c", keep="last")
    return df[["c", "lote", "empresa_lote", "passageiros_dia"]]


def frota_observada(frota: pd.DataFrame) -> pd.Series:
    """Ônibus em operação por linha: média, sobre todos os instantes da coleta, da soma dos dois sentidos."""
    tab = frota.groupby(["instante", "c"]).qv.sum().unstack(fill_value=0)
    return tab.mean().rename("n_media")


def alocar(n0: np.ndarray, a: np.ndarray, m: float = 1.0, perda_max: float = 0.2) -> np.ndarray:
    """Frota inteira ótima com Σn = Σn0 e piso por linha. n0 >= 1 inteiro; a = d·t."""
    n = np.maximum(np.ceil((1 - perda_max) * n0 - 1e-9), 1).astype(int)
    ganho = lambda i: a[i] * (float(n[i]) ** -m - (n[i] + 1.0) ** -m)
    fila = [(-ganho(i), i) for i in range(len(n))]
    heapq.heapify(fila)
    for _ in range(int(n0.sum() - n.sum())):
        _, i = heapq.heappop(fila)
        n[i] += 1
        heapq.heappush(fila, (-ganho(i), i))
    return n


def realocar(tab: pd.DataFrame, perda_max: float = 0.2, h_max: float = 15) -> pd.DataFrame:
    """tab: c, lote, passageiros_dia, ciclo_min, n_atual (inteiro >= 1). Devolve frota recomendada e espera.
    Só entram no ótimo as linhas com intervalo atual <= h_max (onde espera = intervalo/2 vale, hipótese do M1);
    as demais mantêm a frota de hoje."""
    r = tab.assign(no_otimo=tab.ciclo_min / tab.n_atual <= h_max, n_recomendada=tab.n_atual, n_k23=tab.n_atual)
    for _, g in r[r.no_otimo].groupby("lote"):
        a = (g.passageiros_dia * g.ciclo_min).to_numpy()
        n0 = g.n_atual.to_numpy()
        r.loc[g.index, "n_recomendada"] = alocar(n0, a, 1.0, perda_max)
        r.loc[g.index, "n_k23"] = alocar(n0, a, 0.5, perda_max)
    r["delta"] = r.n_recomendada - r.n_atual
    r["espera_antes"] = r.ciclo_min / (2 * r.n_atual)
    r["espera_depois"] = r.ciclo_min / (2 * r.n_recomendada)
    r["espera_depois_k23"] = r.ciclo_min / (2 * r.n_k23)
    return r


def media(x, w) -> float:
    """Média ponderada; NaN se não houver peso."""
    w = w.fillna(0)
    return float(np.average(x, weights=w)) if w.sum() > 0 else np.nan


def resumir_lotes(rea: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por lote, só com as linhas que entraram no ótimo: frota, ônibus movidos, espera antes × depois."""
    return rea[rea.no_otimo].groupby("lote").apply(lambda g: pd.Series({
        "empresa": g.empresa_lote.mode().iat[0], "linhas_no_otimo": len(g), "frota_no_otimo": g.n_atual.sum(),
        "onibus_movidos": g.delta.clip(lower=0).sum(), "linhas_que_ganham": (g.delta > 0).sum(),
        "linhas_que_cedem": (g.delta < 0).sum(),
        "espera_antes": media(g.espera_antes, g.passageiros_dia), "espera_depois": media(g.espera_depois, g.passageiros_dia),
        "espera_depois_k23": media(g.espera_depois_k23, g.passageiros_dia),
        "horas_espera_poupadas_dia": (g.passageiros_dia * (g.espera_antes - g.espera_depois)).sum() / 60}),
        include_groups=False)


def resumir_total(rea: pd.DataFrame) -> dict:
    """Números da cidade inteira (só linhas no ótimo para espera e horas). Horas/dia = estimativa: frota da coleta
    aplicada à demanda do dia inteiro."""
    ot = rea[rea.no_otimo]
    w = ot.passageiros_dia
    return {"lotes": int(ot.lote.nunique()), "linhas": len(rea), "linhas_no_otimo": len(ot),
            "frota": int(rea.n_atual.sum()), "frota_no_otimo": int(ot.n_atual.sum()),
            "onibus_movidos": int(rea.delta.clip(lower=0).sum()),
            "espera_antes_min": round(media(ot.espera_antes, w), 3),
            "espera_depois_min": round(media(ot.espera_depois, w), 3),
            "espera_depois_k23_min": round(media(ot.espera_depois_k23, w), 3),
            "horas_espera_poupadas_dia": round(float((w * (ot.espera_antes - ot.espera_depois)).sum() / 60))}
