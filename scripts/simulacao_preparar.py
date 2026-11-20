"""F4 — Simulação do dia real: prepara o replay e o contrafactual de um lote numa janela da coleta.

Lado "sem" (replay): as posições GPS do Olho Vivo das linhas do lote, como o coletor gravou.
Lado "com" (SIMULAÇÃO): os mesmos traçados do GTFS, com os ônibus igualmente espaçados no ciclo (intervalo
regular), em dois cenários: (A) a frota de hoje (n_atual) e (B) a frota recomendada pelo M2 (n_recomendada),
ambas de realocacao_linha.csv.

Espera medida: as funções do motor (core.frota.regularidade: passagens -> intervalos -> regularidade) aplicadas
só às posições da janela. Espera simulada, com hipóteses declaradas na tela:
  A = intervalo médio medido na janela / 2      (mesmos ônibus e mesma vazão, sem variação: M1 com CV = 0)
  B = A * n_atual / n_recomendada               (mesma velocidade: o intervalo escala com a frota, Lei de Little)
Só entram as linhas do lote que estão no ótimo do M2 (intervalo <= 15 min) e foram medidas na janela.

Uso: python3 scripts/simulacao_preparar.py [--lotes D01,D03] [--janela 17:00-18:00] [--dia 2026-11-19]
Sem --lotes: os 3 lotes que mais poupam em realocacao_lote.csv. --lotes CIDADE junta todos os lotes num arquivo
(use janela de 1 h: o replay da cidade inteira tem ~5 mil ônibus). Grava data/processed/simulacao/.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import GTFS_ZIP, PROC, RAIZ  # noqa: E402
from core.frota import regularidade as R  # noqa: E402

SAIDA = PROC / "simulacao"
DECIMAR = 3      # o traçado do motor é reamostrado a cada 20 m; na tela, um ponto a cada 60 m
CIDADE = "CIDADE"  # --lotes CIDADE: a cidade inteira num arquivo só
MARGEM_S = 300   # lê arquivos um pouco antes e depois da janela (o GPS chega com atraso)


def seg(hhmm: str) -> int:
    p = [int(x) for x in hhmm.split(":")] + [0]
    return p[0] * 3600 + p[1] * 60 + p[2]


def ligar(origem: Path, destino: Path) -> None:
    """Hardlink, senão cópia. No Windows o link simbólico exige privilégio de administrador (WinError 1314) e o
    hardlink só vale dentro do mesmo volume; a cópia é a reserva que funciona sempre (~200 KB por arquivo)."""
    try:
        os.link(origem, destino)
    except (OSError, NotImplementedError, AttributeError):
        shutil.copyfile(origem, destino)


def ler_janela(pasta: Path, ini: int, fim: int):
    """ler_coleta do motor, só com os arquivos da janela (reunidos num diretório temporário)."""
    arqs = [f for f in sorted(pasta.glob("posicao_*.json.gz"))
            if ini - MARGEM_S <= seg(f"{f.stem[8:10]}:{f.stem[10:12]}:{f.stem[12:14]}") <= fim + MARGEM_S]
    if not arqs:
        raise SystemExit(f"nenhum arquivo da coleta na janela em {pasta}")
    with tempfile.TemporaryDirectory() as tmp:      # apagado sozinho ao sair; fora do repositório
        for f in arqs:
            ligar(f.resolve(), Path(tmp) / f.name)
        pos, inst, _ = R.ler_coleta(Path(tmp))
    dentro = (inst >= ini) & (inst <= fim)
    return pos[(pos.t >= ini) & (pos.t <= fim)], inst[dentro], len(arqs)


def latlon(xy: np.ndarray) -> list:
    return np.round(np.c_[xy[:, 1] / R.KY + R.LAT0, xy[:, 0] / R.KX + R.LON0], 5).tolist()


def media(x, w):
    return float(np.average(x, weights=w)) if len(x) and w.sum() > 0 else None


def espera_por_hora(h: pd.DataFrame, lin: pd.DataFrame, ini: int, fim: int) -> list:
    """Espera medida, programada e simulada (A e B) do lote, hora a hora, com as mesmas fórmulas do resumo."""
    h = h[h.c.isin(lin.c)].dropna(subset=["h_prog"])
    base = lin.set_index("c")[["passageiros_dia", "n_atual", "n_recomendada"]]
    saida = []
    for hora, g in h.groupby("hora"):
        a = g.assign(h2=g.h ** 2).groupby("c").agg(n=("h", "size"), sh=("h", "sum"), sh2=("h2", "sum"),
                                                     hm=("h", "mean"), hp=("h_prog", "mean"))
        a = a[a.n >= 4].join(base)
        if a.empty:
            continue
        w = a.passageiros_dia
        regular = a.hm / 2
        saida.append({"hora": int(hora), "linhas": len(a), "intervalos": int(a.n.sum()),
                      "minutos": round((min(fim, (hora + 1) * 3600) - max(ini, hora * 3600)) / 60),
                      "espera_medida": round(media(a.sh2 / (2 * a.sh), w), 3), "espera_programada": round(media(a.hp / 2, w), 3),
                      "espera_regular": round(media(regular, w), 3),
                      "espera_realoc": round(media(regular * a.n_atual / a.n_recomendada, w), 3)})
    return saida


def preparar(lote: str, pos, inst, trac, prog, dur, rea, dia: str, ini: int, fim: int, passo: int = 0) -> dict:
    # CIDADE = todas as linhas frequentes dos 32 lotes juntas; a frota recomendada de cada linha continua sendo a do
    # M2 do próprio lote (nada cruza lote), só a tela e as médias passam a cobrir a cidade toda
    cand = rea[rea.no_otimo & ((rea.lote == lote) | (lote == CIDADE))]
    pos_l = pos[pos.c.isin(cand.c)]
    h = R.intervalos(R.passagens(pos_l, trac), inst, prog)
    reg = R.regularidade(h)
    lin = cand.drop(columns=["cv"], errors="ignore").merge(reg[["c", "intervalos", "h_media", "h_prog", "cv", "espera_real", "espera_prog"]], on="c")
    lin = lin.assign(espera_regular=lin.h_media / 2)
    lin["espera_realoc"] = lin.espera_regular * lin.n_atual / lin.n_recomendada
    lin = lin.sort_values("passageiros_dia", ascending=False).reset_index(drop=True)

    linhas, tracados = [], {}
    for r in lin.itertuples():
        sls = [sl for sl in (1, 2) if (r.c, sl) in trac]
        d = [float(dur.get((r.c, sl), np.nan)) for sl in sls]
        d = [x if x == x and x > 0 else 1.0 for x in d]
        for sl in sls:
            tracados[f"{r.c}|{sl}"] = latlon(trac[(r.c, sl)][0].data[::DECIMAR])
        linhas.append({"c": r.c, "sentidos": sls, "frac_sentido": [round(x / sum(d), 4) for x in d],
                       "comprimento_m": [round(float(trac[(r.c, sl)][1][-1])) for sl in sls],
                       "passageiros_dia": round(r.passageiros_dia), "n_atual": int(r.n_atual),
                       "n_recomendada": int(r.n_recomendada), "ciclo_gtfs_min": r.ciclo_min,
                       "intervalos": int(r.intervalos), "h_media": r.h_media, "h_prog": r.h_prog, "cv": r.cv,
                       "espera_real": r.espera_real, "espera_prog": r.espera_prog,
                       "espera_regular": round(r.espera_regular, 3), "espera_realoc": round(r.espera_realoc, 3)})

    # replay: pontos de cada ônibus [t desde o início da janela, lat, lon, índice da linha * 2 + sentido - 1,
    # metros percorridos no traçado (-1 = a mais de 150 m do traçado; usado só para contar comboio na tela)]
    idx = {c: i for i, c in enumerate(lin.c)}
    rp = pos[pos.c.isin(idx)].copy()
    rp["s"] = -1
    for (c, sl), g in rp.groupby(["c", "sl"]):
        if (c, sl) in trac:
            arv, sg = trac[(c, sl)]
            dist, i = arv.query(R.xy(g.lat, g.lon))
            rp.loc[g.index, "s"] = np.where(dist <= R.DIST_MAX_M, sg[i], -1)
    rp = rp.sort_values(["p", "t"])
    rp = rp.assign(k=rp.c.map(idx) * 2 + rp.sl - 1, t=(rp.t - ini).round().astype(int))
    if passo > 30:      # só para o arquivo não ficar grande demais: uma posição por ônibus a cada `passo` segundos
        rp = rp.assign(bloco=rp.t // passo).drop_duplicates(["p", "bloco"]).drop(columns="bloco")
    onibus = [{"p": int(p), "pts": [[int(a), round(b, 5), round(c, 5), int(k), int(s_)]
                                    for a, b, c, k, s_ in g[["t", "lat", "lon", "k", "s"]].itertuples(index=False)]}
              for p, g in rp.groupby("p")]

    por_hora = espera_por_hora(h, lin, ini, fim)
    w = lin.passageiros_dia
    medida, prog_, regular, realoc = (media(lin[c], w) for c in ("espera_real", "espera_prog", "espera_regular", "espera_realoc"))
    resumo = {"linhas": len(lin), "linhas_candidatas": len(cand), "onibus_no_replay": len(onibus),
              "frota_atual": int(lin.n_atual.sum()), "frota_recomendada": int(lin.n_recomendada.sum()),
              "intervalos_medidos": int(lin.intervalos.sum()),
              "frota_lote_no_otimo": int(cand.n_atual.sum()), "onibus_movidos_lote": int(cand.delta.clip(lower=0).sum()),
              "espera_medida": round(medida, 3), "espera_programada": round(prog_, 3),
              "espera_regular": round(regular, 3), "espera_realoc": round(realoc, 3),
              "ganho_regularizar": round(medida - regular, 3), "ganho_realocar": round(regular - realoc, 3)}
    resumo["razao_regularizar_realocar"] = (round(resumo["ganho_regularizar"] / resumo["ganho_realocar"], 1)
                                            if resumo["ganho_realocar"] > 0 else None)
    empresa = f"todas as empresas ({cand.lote.nunique()} lotes)" if lote == CIDADE else cand.empresa_lote.mode().iat[0]
    return {"versao": 2, "lote": lote, "empresa": empresa, "dia": dia,
            "janela": [ini, fim], "gerado_em": pd.Timestamp.now(tz="America/Sao_Paulo").strftime("%Y-%m-%d %H:%M"),
            "linhas": linhas, "tracados": tracados, "onibus": onibus, "resumo": resumo, "por_hora": por_hora,
            "hipoteses": [
                "Lado esquerdo: replay das posições GPS gravadas do Olho Vivo (o que aconteceu).",
                "Lado direito: SIMULAÇÃO. Mesmos traçados do GTFS, ônibus igualmente espaçados no ciclo, velocidade constante em cada sentido.",
                "Espera medida: intervalos entre passagens a 25%, 50% e 75% do traçado na janela (motor, M1): ΣH²/(2ΣH).",
                "Cenário A, só regularizar: mesma frota e mesmo intervalo médio medido, sem variação: espera = intervalo médio / 2.",
                "Cenário B, regularizar + realocar: frota do M2 no lote (n recomendada, piso de 20%); intervalo × n atual / n recomendada.",
                "Médias ponderadas pelos passageiros/dia da planilha da SPTrans (set/2026). Só linhas no ótimo (intervalo ≤ 15 min) medidas na janela.",
                "Comboio na tela: dois ônibus da mesma linha e sentido a menos de 25% do espaçamento regular (comprimento do ciclo ÷ n atual), fora dos 5% iniciais e finais do traçado (regra do M3, em distância). Só ilustra; não entra nas esperas.",
                "Por hora: mesmas fórmulas, só com os intervalos que terminam naquela hora, nas linhas com 4 ou mais intervalos na hora.",
                f"Janela de {(fim - ini) / 3600:.0f} h: intervalos maiores que a janela não aparecem (viés do P25)."]
            + ([f"Para o arquivo caber no navegador, o replay mostra uma posição por ônibus a cada {passo} s (o GPS grava a cada 30 s); "
                "as esperas são calculadas com todas as posições, não com as amostradas."] if passo > 30 else [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lotes", default="")
    ap.add_argument("--janela", default="14:00-15:00")
    ap.add_argument("--dia", default="")
    ap.add_argument("--passo", type=int, default=0, help="segundos entre posições no replay (0 = todas)")
    a = ap.parse_args()
    dias = sorted(p for p in (RAIZ / "data/olhovivo").glob("20*") if p.is_dir())
    pasta = RAIZ / "data/olhovivo" / a.dia if a.dia else dias[-1]
    ini, fim = (seg(x) for x in a.janela.split("-"))
    rea = pd.read_csv(PROC / "realocacao_linha.csv")
    rl = pd.read_csv(PROC / "realocacao_lote.csv").set_index("lote").horas_espera_poupadas_dia
    lotes = a.lotes.split(",") if a.lotes else rl.nlargest(3).index.tolist()
    trac, prog, dur = R.ler_gtfs(GTFS_ZIP)
    dur = dur.groupby(["route_id", "sl"]).duracao_min.mean().to_dict()
    pos, inst, narq = ler_janela(pasta, ini, fim)
    SAIDA.mkdir(exist_ok=True)
    for lote in lotes:
        sim = preparar(lote, pos, inst, trac, prog, dur, rea, pasta.name, ini, fim, a.passo)
        horas = float(rl.sum() if lote == CIDADE else rl.get(lote, np.nan))                 # M2 do motor, coleta inteira
        sim["resumo"]["horas_poupadas_dia_motor"] = round(horas) if horas == horas else None
        nome = f"sim_{pasta.name}_{lote}_{a.janela.replace(':', '').replace('-', '_')}.json"
        sim["resumo"]["passo_replay_s"] = passo if (passo := a.passo) > 30 else 30
        (SAIDA / nome).write_text(json.dumps(sim, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(nome, f"{(SAIDA / nome).stat().st_size / 1e6:.1f} MB", json.dumps(sim["resumo"], ensure_ascii=False))
    print(f"{narq} arquivos da coleta, {len(inst)} instantes na janela")


if __name__ == "__main__":
    main()
