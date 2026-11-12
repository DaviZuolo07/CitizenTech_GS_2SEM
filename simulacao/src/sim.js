// Lógica da simulação, sem nada de tela. A mesma regra do produto: demanda pelo modelo treinado,
// alvo inteiro pelo maior resto, piso de cobertura e matriz T coluna-estocástica.

// Regressão logística treinada na Pesquisa OD 2017 (modelo de 4 variáveis, docs/08 e entregas/mlam/03).
export const MODELO = { intercepto: 2.5304, log_renda_pc: -0.4280, qt_auto: -0.6436, distancia_km: 0.0164, idade: -0.0062 };
// Embarques de ônibus por hora de saída na OD 2017 (soma expandida), das 0h às 23h: dá a forma do dia.
export const EMBARQUES_HORA = [17095, 6917, 5201, 9121, 261530, 560965, 1077495, 713564, 454620, 306565, 323063, 422589,
  602374, 391941, 388354, 416770, 615904, 948100, 867964, 340415, 189508, 166271, 450402, 133303];

// Cidade fictícia: 6 bairros ligados ao Centro. desloc = horas que o pico do bairro adianta (-) ou atrasa (+).
export const BAIRROS = [
  { nome: "Jardim Norte", x: 5, z: -62, trabalhadores: 5200, renda_pc: 1100, carros: 0.4, km: 14, desloc: -1, cor: 0xe07a5f },
  { nome: "Vila Leste", x: 70, z: -12, trabalhadores: 4600, renda_pc: 1300, carros: 0.5, km: 12, desloc: -1, cor: 0xf2cc8f },
  { nome: "Parque Sul", x: 22, z: 64, trabalhadores: 4200, renda_pc: 1600, carros: 0.7, km: 10, desloc: 0, cor: 0x81b29a },
  { nome: "Alto Oeste", x: -66, z: 6, trabalhadores: 5600, renda_pc: 6500, carros: 1.8, km: 7, desloc: 1, cor: 0x9d8ac7 },
  { nome: "Morada Nova", x: -44, z: -50, trabalhadores: 3000, renda_pc: 2400, carros: 1.0, km: 9, desloc: 0, cor: 0x6fa8dc },
  { nome: "Lago Azul", x: -36, z: 56, trabalhadores: 3600, renda_pc: 4000, carros: 1.5, km: 8, desloc: 1, cor: 0xd5a6bd },
];
export const P = { frota: 36, capacidade: 40, kmh: 20, inicio: 5, fim: 23, perdaMaxima: 0.2, idade: 38, passo: 0.25, custoKm: 10 };

export const probOnibus = (b) => {
  const z = MODELO.intercepto + MODELO.log_renda_pc * Math.log(b.renda_pc) + MODELO.qt_auto * b.carros + MODELO.distancia_km * b.km + MODELO.idade * P.idade;
  return 1 / (1 + Math.exp(-z));
};

export function maiorResto(pesos, total) {
  const soma = pesos.reduce((a, b) => a + b, 0);
  if (total === 0 || soma === 0) return pesos.map(() => 0);
  const cotas = pesos.map((p) => (p * total) / soma), base = cotas.map(Math.floor);
  const sobra = total - base.reduce((a, b) => a + b, 0);
  cotas.map((c, i) => [base[i] - c, i]).sort((a, b) => a[0] - b[0] || a[1] - b[1]).slice(0, sobra).forEach(([, i]) => base[i]++);
  return base;
}

export function alvoProporcional(x, necessidade, perdaMaxima = 1) {
  const total = x.reduce((a, b) => a + b, 0), piso = x.map((v) => Math.ceil((1 - perdaMaxima) * v - 1e-9));
  if (necessidade.reduce((a, b) => a + b, 0) === 0) return [...x];
  const preso = x.map(() => false);
  let ideal = piso.map(Number);
  while (preso.includes(false)) {
    const livre = total - piso.reduce((a, v, i) => a + (preso[i] ? v : 0), 0);
    const somaNec = necessidade.reduce((a, v, i) => a + (preso[i] ? 0 : v), 0);
    ideal = necessidade.map((n) => (n * livre) / somaNec);
    const novos = ideal.map((v, i) => !preso[i] && v < piso[i] - 1e-9);
    if (!novos.includes(true)) break;
    novos.forEach((n, i) => { if (n) preso[i] = true; });
  }
  const excesso = ideal.map((v, i) => (preso[i] ? 0 : v - piso[i]));
  const extra = maiorResto(excesso, total - piso.reduce((a, b) => a + b, 0));
  return piso.map((v, i) => v + extra[i]);
}

export function matrizT(x, alvo) {
  const n = x.length, sobra = x.map((v, i) => Math.max(v - alvo[i], 0)), falta = x.map((v, i) => Math.max(alvo[i] - v, 0));
  const totalFalta = falta.reduce((a, b) => a + b, 0);
  return x.map((_, i) => x.map((xj, j) => {
    const cedido = xj > 0 ? sobra[j] / xj : 0;
    return (i === j ? 1 - cedido : 0) + (totalFalta > 0 ? (falta[i] / totalFalta) * cedido : 0);
  }));
}

const rng = (semente) => () => { // mulberry32: mesma semente = mesmas chegadas nos dois mundos
  let t = (semente += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const poisson = (media, r) => { let k = 0, p = Math.exp(-media), s = p; const u = r(); while (u > s) { k++; p *= media / k; s += p; } return k; };

const somaDia = EMBARQUES_HORA.slice(P.inicio, P.fim).reduce((a, b) => a + b, 0);
// Passageiros por minuto no bairro k, na hora h, no sentido (0 = bairro→centro, 1 = centro→bairro).
export function taxa(b, h, sentido) {
  const hh = Math.min(Math.max(Math.floor(h) - b.desloc, 0), 23);
  const fracaoHora = EMBARQUES_HORA[hh] / somaDia;
  const paraCentro = h < 12 ? 0.85 : 0.15;
  return (b.trabalhadores * probOnibus(b) * 2 * fracaoHora * (sentido === 0 ? paraCentro : 1 - paraCentro)) / 60;
}
const ida = (b) => (b.km / P.kmh) * 60;                       // minutos de um sentido
export const necessidade = (h) => BAIRROS.map((b) => (taxa(b, h, 0) + taxa(b, h, 1)) * ida(b)); // passageiros a bordo esperados

export class Mundo {
  constructor(comLinhaCerta, frotaTotal = P.frota) {
    this.inteligente = comLinhaCerta; this.r = rng(2026); this.t = P.inicio * 60; this.hora = -1;
    const porPopulacao = maiorResto(BAIRROS.map((b) => b.trabalhadores), frotaTotal);   // oferta fixa, proporcional à população
    // o dia inteligente já começa planejado para o primeiro pico, sem tirar mais de 60% de nenhum bairro
    this.frota = comLinhaCerta ? alvoProporcional(porPopulacao, necessidade(P.inicio + 1), 0.6) : porPopulacao;
    this.filas = BAIRROS.map(() => [[], []]);
    this.onibus = [];
    this.frota.forEach((n, k) => { for (let i = 0; i < n; i++) this.onibus.push({ linha: k, fase: i / n, carga: 0, destino: null }); });
    this.m = { esperaSoma: 0, embarcados: 0, entregues: 0, km: 0, lugarKm: 0, passKm: 0, maiorFila: 0 };
    this.eventos = []; this.T = null;
  }
  get fim() { return this.t >= P.fim * 60; }
  planejar(h) { // a cada hora, o mundo inteligente recalcula o alvo e marca os ônibus que mudam de linha
    const alvo = alvoProporcional(this.frota, necessidade(h), P.perdaMaxima);
    this.T = matrizT(this.frota, alvo);
    const falta = alvo.map((a, k) => a - this.frota[k]); this.eventos = [];
    this.onibus.forEach((o) => (o.destino = null));
    falta.forEach((f, k) => {
      if (f >= 0) return;
      const sem = this.onibus.filter((o) => o.linha === k).sort((a, b) => ((0.5 - a.fase + 1) % 1) - ((0.5 - b.fase + 1) % 1)).slice(0, -f);
      sem.forEach((o) => { const j = falta.findIndex((v) => v > 0); falta[j]--; o.destino = j; this.eventos.push([k, j]); });
    });
  }
  embarcar(o, sentido) {
    const fila = this.filas[o.linha][sentido];
    while (fila.length && o.carga < P.capacidade) { this.m.esperaSoma += this.t - fila.shift(); this.m.embarcados++; o.carga++; }
  }
  passo(dt = P.passo) {
    if (this.fim) return;
    const h = Math.floor(this.t / 60);
    if (h !== this.hora) { this.hora = h; if (this.inteligente) this.planejar(h); }
    BAIRROS.forEach((b, k) => [0, 1].forEach((s) => { for (let i = poisson(taxa(b, h, s) * dt, this.r); i > 0; i--) this.filas[k][s].push(this.t); }));
    for (const o of this.onibus) {
      const b = BAIRROS[o.linha], antes = o.fase, avanco = dt / (2 * ida(b));
      o.fase = (o.fase + avanco) % 1;
      const km = avanco * 2 * b.km; this.m.km += km; this.m.lugarKm += km * P.capacidade; this.m.passKm += km * o.carga;
      if (antes < 0.5 && o.fase >= 0.5) {                       // chegou ao Centro
        this.m.entregues += o.carga; o.carga = 0;
        if (o.destino !== null) { this.frota[o.linha]--; o.linha = o.destino; this.frota[o.linha]++; o.destino = null; o.fase = 0.5; }
        this.embarcar(o, 1);
      } else if (o.fase < antes) { this.m.entregues += o.carga; o.carga = 0; this.embarcar(o, 0); } // chegou ao bairro
    }
    this.m.maiorFila = Math.max(this.m.maiorFila, ...this.filas.flat().map((f) => f.length));
    this.t += dt;
  }
  resumo() {
    const esperando = this.filas.flat().reduce((a, f) => a + f.length, 0), m = this.m;
    return { esperaMedia: m.embarcados ? m.esperaSoma / m.embarcados : 0, esperando, maiorFila: m.maiorFila, transportados: m.embarcados,
      ocupacao: m.lugarKm ? m.passKm / m.lugarKm : 0, lugarKmOcioso: m.lugarKm - m.passKm, km: m.km,
      custoPorPassageiro: m.embarcados ? (m.km * P.custoKm) / m.embarcados : 0 };
  }
}

// Quantos ônibus a mais a operação fixa precisaria para chegar à mesma espera média do dia inteligente.
export function frotaEquivalente(esperaAlvo, limite = 3 * P.frota) {
  for (let f = P.frota; f <= limite; f++) {
    const m = new Mundo(false, f);
    while (!m.fim) m.passo();
    if (m.resumo().esperaMedia <= esperaAlvo) return f;
  }
  return null;
}
