import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { BAIRROS, EMBARQUES_HORA, Mundo, P, frotaEquivalente, probOnibus } from "./sim.js";

const $ = (id) => document.getElementById(id);
const tela = $("tela");
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
const camera = new THREE.PerspectiveCamera(42, 1, 1, 1000);
camera.position.set(0, 128, 178);
const controles = new OrbitControls(camera, tela);
controles.target.set(0, 0, 22); controles.maxPolarAngle = 1.45; controles.minDistance = 60; controles.maxDistance = 380; controles.enableDamping = true;

const MAX_PESSOAS = 160, caixa = new THREE.BoxGeometry(1, 1, 1);
const corOcupacao = (f) => new THREE.Color().setHSL(0.33 * (1 - Math.min(f, 1)), 0.75, 0.48);   // verde vazio -> vermelho lotado
const lane = (b, lado) => { const n = Math.hypot(b.x, b.z); return new THREE.Vector3((-b.z / n) * lado, 0, (b.x / n) * lado); };

function rotulo(texto, cor = "#1d2733", escala = 15) {
  const c = document.createElement("canvas"); c.width = 512; c.height = 128;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false }));
  s.scale.set(escala * 4, escala, 1);
  s.escrever = (t) => {
    const g = c.getContext("2d"); g.clearRect(0, 0, 512, 128);
    g.font = "800 54px system-ui, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    g.lineWidth = 12; g.lineJoin = "round"; g.strokeStyle = "#ffffff"; g.strokeText(t, 256, 64); g.fillStyle = cor; g.fillText(t, 256, 64);
    s.material.map.needsUpdate = true;
  };
  s.escrever(texto); return s;
}

function predios(grupo, cx, cz, raio, n, cor, alturaMax, semente) {
  let r = semente; const rnd = () => ((r = (r * 16807) % 2147483647) / 2147483647);
  const m = new THREE.InstancedMesh(caixa, new THREE.MeshLambertMaterial({ color: cor }), n), d = new THREE.Object3D();
  for (let i = 0; i < n; i++) {
    const a = rnd() * 6.283, q = 5 + Math.sqrt(rnd()) * raio, h = 2 + rnd() * alturaMax;
    d.position.set(cx + Math.cos(a) * q, h / 2, cz + Math.sin(a) * q); d.scale.set(2.4 + rnd() * 2.5, h, 2.4 + rnd() * 2.5); d.rotation.y = rnd(); d.updateMatrix();
    m.setMatrixAt(i, d.matrix);
  }
  m.castShadow = true; grupo.add(m);
}

class Cena {
  constructor(mundo) {
    this.mundo = mundo; this.cena = new THREE.Scene(); this.cena.background = new THREE.Color(mundo.inteligente ? 0xe8f1f8 : 0xf6efe6);
    this.cena.add(new THREE.HemisphereLight(0xffffff, 0x8a8f7a, 1.15));
    const sol = new THREE.DirectionalLight(0xffffff, 1.4); sol.position.set(70, 130, 50); sol.castShadow = true;
    Object.assign(sol.shadow.camera, { left: -130, right: 130, top: 130, bottom: -130 }); sol.shadow.mapSize.set(2048, 2048); this.cena.add(sol);
    const chao = new THREE.Mesh(new THREE.CircleGeometry(125, 64), new THREE.MeshLambertMaterial({ color: 0xb9d3a4 }));
    chao.rotation.x = -Math.PI / 2; chao.receiveShadow = true; this.cena.add(chao);
    predios(this.cena, 0, 0, 13, 46, 0x8d99ae, 20, 7);
    const centro = rotulo("Centro", "#1d2733", 11); centro.position.set(0, 30, 0); this.cena.add(centro);
    this.filas = []; this.textos = [];
    BAIRROS.forEach((b, k) => {
      predios(this.cena, b.x, b.z, 9 + b.trabalhadores / 600, 16 + Math.round(b.trabalhadores / 260), b.cor, 4 + b.renda_pc / 900, 11 + k);
      const comp = Math.hypot(b.x, b.z), via = new THREE.Mesh(caixa, new THREE.MeshLambertMaterial({ color: 0x59616e }));
      via.scale.set(comp, 0.2, 5); via.position.set(b.x / 2, 0.1, b.z / 2); via.rotation.y = -Math.atan2(b.z, b.x); via.receiveShadow = true; this.cena.add(via);
      const t = rotulo(b.nome, "#1d2733", 9); t.position.set(b.x * 1.16, 17, b.z * 1.16); this.cena.add(t);
      [0, 1].forEach((s) => {   // fila no bairro (s=0) e no Centro (s=1)
        const m = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.42, 0.9, 2, 6), new THREE.MeshLambertMaterial({ color: s ? 0x3d405b : 0x23395b }), MAX_PESSOAS);
        const f = s ? 0.2 : 0.9, base = new THREE.Vector3(b.x * f, 0, b.z * f).add(lane(b, 5)), ao = new THREE.Vector3(b.x, 0, b.z).normalize(), lado = lane(b, 1), d = new THREE.Object3D();
        for (let i = 0; i < MAX_PESSOAS; i++) {
          d.position.copy(base).addScaledVector(lado, Math.floor(i / 10) * 1.05).addScaledVector(ao, ((i % 10) - 4.5) * 1.05 * (s ? 1 : -1)); d.position.y = 0.95; d.updateMatrix(); m.setMatrixAt(i, d.matrix);
        }
        m.count = 0; this.cena.add(m);
        const n = rotulo("", "#b3261e", 9); n.position.copy(base).addScaledVector(lado, 9); n.position.y = 7; this.cena.add(n);
        this.filas.push([m, n, k, s, -1]);
      });
    });
    this.onibus = mundo.onibus.map(() => {
      const g = new THREE.Mesh(caixa, new THREE.MeshLambertMaterial({ color: 0x2a9d8f })); g.scale.set(5.4, 2.3, 2.3); g.castShadow = true; this.cena.add(g); return g;
    });
  }
  atualizar() {
    this.mundo.onibus.forEach((o, i) => {
      const b = BAIRROS[o.linha], indo = o.fase < 0.5, u = indo ? 1 - o.fase * 2 : (o.fase - 0.5) * 2, g = this.onibus[i];
      g.position.set(b.x * (0.06 + 0.86 * u), 1.4, b.z * (0.06 + 0.86 * u)).add(lane(b, indo ? -1.3 : 1.3));
      g.rotation.y = -Math.atan2(b.z, b.x); g.material.color.copy(o.destino !== null ? new THREE.Color(0x7b2cbf) : corOcupacao(o.carga / P.capacidade));
    });
    for (const f of this.filas) {
      const n = this.mundo.filas[f[2]][f[3]].length;
      if (n !== f[4]) { f[4] = n; f[0].count = Math.min(n, MAX_PESSOAS); f[1].escrever(n >= 12 ? String(n) : ""); }
    }
  }
}

let mundos, cenas, velocidade = 1, pausado = false, equivalente = null;
function reiniciar() {
  mundos = [new Mundo(false), new Mundo(true)]; cenas = mundos.map((m) => new Cena(m)); equivalente = null; $("fim").hidden = true;
}
const nf = (v, d = 0) => v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const LINHAS = [
  ["Espera média no ponto", (r) => r.esperaMedia, (v) => nf(v, 1) + " min", -1],
  ["Pessoas esperando agora", (r) => r.esperando, (v) => nf(v), -1],
  ["Maior fila do dia", (r) => r.maiorFila, (v) => nf(v), -1],
  ["Passageiros transportados", (r) => r.transportados, (v) => nf(v), 1],
  ["Ocupação média dos ônibus", (r) => r.ocupacao * 100, (v) => nf(v) + "%", 0],
  ["Km rodados pela frota", (r) => r.km, (v) => nf(v) + " km", 0],
];
function painel() {
  const [a, b] = mundos.map((m) => m.resumo()), h = mundos[0].t / 60;
  $("relogio").textContent = `${String(Math.floor(h)).padStart(2, "0")}:${String(Math.floor((h % 1) * 60)).padStart(2, "0")}`;
  $("placar").innerHTML = LINHAS.map(([nome, f, fmt, sinal]) => {
    const x = f(a), y = f(b), dif = x ? ((y - x) / x) * 100 : 0, bom = sinal && Math.abs(dif) >= 1 ? (Math.sign(dif) === sinal ? "bom" : "ruim") : "";
    return `<tr><th>${nome}</th><td>${fmt(x)}</td><td>${fmt(y)}</td><td class="${bom}">${Math.abs(dif) < 1 ? "igual" : (dif > 0 ? "+" : "−") + nf(Math.abs(dif)) + "%"}</td></tr>`;
  }).join("");
  $("frota").innerHTML = BAIRROS.map((bb, k) => `<tr><th><i style="background:#${bb.cor.toString(16).padStart(6, "0")}"></i>${bb.nome}</th><td>${nf(bb.renda_pc)}</td><td>${nf(bb.carros, 1)}</td>
    <td>${nf(probOnibus(bb) * 100)}%</td><td>${mundos[0].frota[k]}</td><td><b>${mundos[1].frota[k]}</b></td></tr>`).join("");
  const ev = mundos[1].eventos.reduce((o, [de, para]) => ((o[de + ">" + para] = (o[de + ">" + para] || 0) + 1), o), {});
  $("eventos").innerHTML = Object.entries(ev).map(([k, n]) => { const [de, para] = k.split(">"); return `<li>${n} ônibus: ${BAIRROS[de].nome} → ${BAIRROS[para].nome}</li>`; }).join("") || "<li>frota mantida nesta hora</li>";
  $("barra").style.width = `${((mundos[0].t / 60 - P.inicio) / (P.fim - P.inicio)) * 100}%`;
  if (mundos[0].fim && equivalente === null) {
    equivalente = frotaEquivalente(b.esperaMedia) ?? 0;
    const extra = equivalente - P.frota, km = (a.km / P.frota) * extra;
    $("fimTexto").innerHTML = `Com a <b>mesma frota de ${P.frota} ônibus</b>, a espera média caiu de <b>${nf(a.esperaMedia, 1)}</b> para <b>${nf(b.esperaMedia, 1)} min</b>
      e a maior fila, de <b>${nf(a.maiorFila)}</b> para <b>${nf(b.maiorFila)}</b> pessoas.<br>Para chegar a essa espera sem redistribuir, a operação fixa precisaria de
      <b>${extra > 0 ? extra + " ônibus a mais" : "nenhum ônibus a mais"}</b>${extra > 0 ? ` (${nf(km)} km por dia; a R$ ${nf(P.custoKm)}/km de custo ilustrativo, R$ ${nf(km * P.custoKm)} por dia)` : ""}.`;
    $("fim").hidden = false;
  }
}

let anterior = performance.now(), acumulado = 0, quadro = 0;
function loop(agora) {
  requestAnimationFrame(loop);
  const dt = Math.min((agora - anterior) / 1000, 0.1); anterior = agora;
  if (!pausado) { acumulado += dt * 12 * velocidade; while (acumulado >= P.passo) { mundos.forEach((m) => m.passo()); acumulado -= P.passo; } }   // 1 s = 12 min simulados
  controles.update();
  const L = tela.clientWidth, A = tela.clientHeight;
  if (tela.width !== Math.floor(L * renderer.getPixelRatio()) || tela.height !== Math.floor(A * renderer.getPixelRatio())) renderer.setSize(L, A, false);
  const empilhado = L < 820, vw = empilhado ? L : L / 2, vh = empilhado ? A / 2 : A;
  camera.aspect = vw / vh; camera.updateProjectionMatrix(); renderer.setScissorTest(true);
  cenas.forEach((c, i) => { c.atualizar(); const x = empilhado ? 0 : i * vw, y = empilhado ? (1 - i) * vh : 0; renderer.setViewport(x, y, vw, vh); renderer.setScissor(x, y, vw, vh); renderer.render(c.cena, camera); });
  if (quadro++ % 10 === 0) painel();
}
$("pausa").onclick = () => { pausado = !pausado; $("pausa").textContent = pausado ? "Continuar" : "Pausar"; };
$("reinicio").onclick = reiniciar; $("denovo").onclick = reiniciar;
document.querySelectorAll("[data-v]").forEach((b) => (b.onclick = () => { velocidade = +b.dataset.v; document.querySelectorAll("[data-v]").forEach((x) => x.classList.toggle("ativo", x === b)); }));
$("detalhes").onclick = () => document.body.classList.toggle("fechado");
window.__sim = { get mundos() { return mundos; }, avancar(min) { for (let i = 0; i < min / P.passo; i++) mundos.forEach((m) => m.passo()); painel(); } };
reiniciar(); requestAnimationFrame(loop);
