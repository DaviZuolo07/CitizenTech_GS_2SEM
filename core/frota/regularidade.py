"""F1 — Regularidade medida com o Olho Vivo (M1 e M3 do caderno).

Passagem: cada posição é projetada no traçado GTFS da linha-sentido (ponto mais próximo do traçado reamostrado
a cada 20 m). A passagem num ponto de controle (25%, 50% e 75% do traçado) é o instante interpolado em que a
distância percorrida pelo ônibus cruza aquele ponto. Intervalo = diferença entre passagens consecutivas no mesmo
ponto. Espera com chegada aleatória: AWT = ΣH² / (2ΣH); programada SWT = média do intervalo programado / 2.
"""
import gzip
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

LAT0, LON0 = -23.55, -46.63
KX, KY = 111_320 * np.cos(np.radians(LAT0)), 110_540   # metros por grau
PASSO_M = 20          # reamostragem do traçado
DIST_MAX_M = 150      # posição mais longe que isso do traçado é descartada (garagem, desvio)
VEL_MAX = 25          # m/s; salto maior entre duas posições é erro de projeção
DT_MAX = 180          # s; posições mais espaçadas não interpolam passagem
BURACO_COLETA = 120   # s; intervalo que atravessa um buraco da coleta é descartado
PONTOS = (0.25, 0.5, 0.75)
COMBOIO = 0.25        # intervalo < 25% do programado = comboio (M3)
LIMITE_EWT = 15       # min; Londres só usa espera excessiva em linhas com intervalo programado <= 15 min
MIN_INTERVALOS = 10   # linha com menos intervalos medidos não é publicada


def xy(lat, lon):
    return np.c_[(np.asarray(lon) - LON0) * KX, (np.asarray(lat) - LAT0) * KY]


def ler_coleta(pasta: Path):
    """Posições únicas (linha, sentido, ônibus, hora do GPS), instantes da coleta e ônibus por linha em cada instante.
    Cada arquivo vira um bloco compacto (hora em segundos desde a meia-noite local) para caber o dia inteiro."""
    blocos, frota, instantes = [], [], []
    for f in sorted(Path(pasta).glob("posicao_*.json.gz")):
        try:
            d = json.load(gzip.open(f))
        except (OSError, ValueError):   # arquivo ainda sendo gravado
            continue
        inst = d["coletado_em"]
        instantes.append(inst)
        ls = (d.get("resposta") or {}).get("l") or []
        frota += [(inst, l["c"], l["qv"]) for l in ls]
        b = pd.DataFrame([(l["c"], l["sl"], v["p"], v["ta"], v["py"], v["px"]) for l in ls for v in l.get("vs") or []],
                         columns=["c", "sl", "p", "ta", "lat", "lon"])
        hora = pd.to_datetime(b.pop("ta"), utc=True, format="ISO8601").dt.tz_convert("America/Sao_Paulo").dt.tz_localize(None)
        b["t"] = (hora - hora.dt.normalize()).dt.total_seconds()   # segundos desde a meia-noite local
        blocos.append(b.drop_duplicates(["c", "sl", "p", "t"]))
    pos = pd.concat(blocos, ignore_index=True).drop_duplicates(["c", "sl", "p", "t"])
    inst = pd.to_datetime(pd.Series(instantes))
    return pos, (inst - inst.dt.normalize()).dt.total_seconds().sort_values().to_numpy(), \
        pd.DataFrame(frota, columns=["instante", "c", "qv"])


def ler_gtfs(caminho: Path):
    """Traçado (KD-tree + distância acumulada) por (linha, sentido), intervalo programado por hora e duração da viagem."""
    z = zipfile.ZipFile(caminho)
    trips = pd.read_csv(z.open("trips.txt"), usecols=["route_id", "trip_id", "direction_id", "shape_id"])
    trips["sl"] = trips.direction_id + 1                      # Olho Vivo: sentido 1/2 = direction_id 0/1
    st = pd.read_csv(z.open("stop_times.txt"), usecols=["trip_id", "arrival_time"])
    seg = st.arrival_time.str.split(":", expand=True).astype(int) @ np.array([3600, 60, 1])
    trips["duracao_min"] = trips.trip_id.map(seg.groupby(st.trip_id).agg(np.ptp) / 60)
    fq = pd.read_csv(z.open("frequencies.txt"))
    fq["hora"] = fq.start_time.str[:2].astype(int)
    prog = fq.assign(h_prog=fq.headway_secs / 60).merge(trips, on="trip_id")[["route_id", "sl", "hora", "h_prog"]]
    sh = pd.read_csv(z.open("shapes.txt"), usecols=["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"])
    arvores = {}
    for sid, g in sh.sort_values(["shape_id", "shape_pt_sequence"]).groupby("shape_id"):
        p = xy(g.shape_pt_lat, g.shape_pt_lon)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
        s = np.arange(0, d[-1], PASSO_M)
        arvores[sid] = (cKDTree(np.c_[np.interp(s, d, p[:, 0]), np.interp(s, d, p[:, 1])]), s)
    trac = {(r.route_id, r.sl): arvores[r.shape_id] for r in trips.itertuples() if r.shape_id in arvores}
    return trac, prog, trips[["route_id", "sl", "duracao_min"]]


def passagens(pos: pd.DataFrame, trac: dict) -> pd.DataFrame:
    """Instantes em que cada ônibus cruza os pontos de controle do seu traçado."""
    saida = []
    for (c, sl), g in pos.groupby(["c", "sl"]):
        if (c, sl) not in trac:
            continue
        arv, s = trac[(c, sl)]
        dist, i = arv.query(xy(g.lat, g.lon))
        g = g.assign(s=s[i])[dist <= DIST_MAX_M].sort_values(["p", "t"])
        p, t, d = g.p.to_numpy(), g.t.to_numpy(), g.s.to_numpy()
        dt, ds = np.diff(t), np.diff(d)
        ok = (p[1:] == p[:-1]) & (dt > 0) & (dt <= DT_MAX) & (ds > 0) & (ds <= VEL_MAX * dt)
        for frac in PONTOS:
            alvo = frac * s[-1]
            k = np.flatnonzero(ok & (d[:-1] < alvo) & (d[1:] >= alvo))
            tp = t[k] + (alvo - d[k]) / ds[k] * dt[k]
            saida.append(pd.DataFrame({"c": c, "sl": sl, "ponto": frac, "p": p[k], "t": tp}))
    return pd.concat(saida, ignore_index=True)


def intervalos(pas: pd.DataFrame, instantes: np.ndarray, prog: pd.DataFrame) -> pd.DataFrame:
    """Intervalo entre passagens consecutivas no mesmo ponto, com o intervalo programado da hora."""
    pas = pas.sort_values(["c", "sl", "ponto", "t"])
    t0 = pas.groupby(["c", "sl", "ponto"]).t.shift()
    h = pas.assign(t0=t0, h=(pas.t - t0) / 60).dropna(subset=["t0"])
    gap = np.diff(instantes) > BURACO_COLETA                 # buracos da coleta: [instantes[i], instantes[i+1]]
    ini, fim = instantes[:-1][gap], instantes[1:][gap]
    atravessa = np.searchsorted(ini, h.t.to_numpy()) > np.searchsorted(fim, h.t0.to_numpy(), side="right")
    h = h[~atravessa].assign(hora=(h.t // 3600).astype(int))
    return h.merge(prog.rename(columns={"route_id": "c"}), on=["c", "sl", "hora"], how="left")


def regularidade(h: pd.DataFrame) -> pd.DataFrame:
    """M1 e M3 por linha (os dois sentidos e os três pontos juntos)."""
    h = h.dropna(subset=["h_prog"])
    prog_hora = h.drop_duplicates(["c", "sl", "hora"]).groupby("c").h_prog.mean()
    r = h.assign(h2=h.h ** 2, comboio=h.h < COMBOIO * h.h_prog).groupby("c").agg(
        intervalos=("h", "size"), h_media=("h", "mean"), h_dp=("h", "std"), sh=("h", "sum"), sh2=("h2", "sum"),
        comboio=("comboio", "mean"), hora_ini=("hora", "min"), hora_fim=("hora", "max"))
    r["h_prog"] = prog_hora
    r["cv"] = r.h_dp / r.h_media
    r["espera_real"] = r.sh2 / (2 * r.sh)                    # AWT
    r["espera_prog"] = r.h_prog / 2                          # SWT
    r["espera_excessiva"] = r.espera_real - r.espera_prog    # EWT
    r["alta_frequencia"] = r.h_prog <= LIMITE_EWT
    r = r[r.intervalos >= MIN_INTERVALOS].drop(columns=["h_dp", "sh", "sh2"])
    return r.round(3).reset_index()
