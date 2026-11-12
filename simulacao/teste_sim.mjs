import { frotaEquivalente, Mundo, BAIRROS, P, probOnibus, alvoProporcional, matrizT, maiorResto, necessidade } from "./src/sim.js";
const ok = (c, m) => { if (!c) throw new Error("FALHOU: " + m); };
ok(maiorResto([1, 1, 1], 10).reduce((a, b) => a + b) === 10, "maior resto soma");
ok(JSON.stringify(alvoProporcional([100, 100, 100], [1, 1, 10], 0.2)) === "[80,80,140]", "piso igual ao do Python");
ok(JSON.stringify(alvoProporcional([12, 20, 16, 24], [14, 19, 18, 21])) === "[14,19,18,21]", "caso MMC");
const T = matrizT([12, 20, 16, 24], [14, 19, 18, 21]);
ok(T[0].map((_, j) => T.reduce((a, l) => a + l[j], 0)).every((s) => Math.abs(s - 1) < 1e-9), "colunas de T somam 1");
ok(Math.abs(T[0][1] - 0.025) < 1e-9 && Math.abs(T[3][3] - 0.875) < 1e-9, "T igual à do notebook da MMC");
console.log("P(ônibus):", BAIRROS.map((b) => `${b.nome} ${probOnibus(b).toFixed(3)}`).join(" | "));
const [a, b] = [new Mundo(false), new Mundo(true)];
console.log("frota inicial sem:", a.frota.join(","), "| com:", b.frota.join(","), "| necessidade 6h:", necessidade(6).map((v) => v.toFixed(0)).join(","));
while (!a.fim) { a.passo(); b.passo(); if (a.t % 180 === 0) console.log((a.t / 60) + "h", "esperando", a.resumo().esperando, b.resumo().esperando, "| frota com:", b.frota.join(",")); }
ok(a.onibus.length === P.frota && b.onibus.length === P.frota && b.frota.reduce((x, y) => x + y) === P.frota, "frota preservada");
const fmt = (r) => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, +v.toFixed(2)]));
console.log("SEM", fmt(a.resumo())); console.log("COM", fmt(b.resumo()));
const eq = frotaEquivalente(b.resumo().esperaMedia);
console.log("frota fixa equivalente:", eq, "| a mais:", eq - P.frota);
