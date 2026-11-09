# Simulação 3D (opcional — só para o pitch)

## Veredito: viável na versão "leve", inviável na versão "jogo"
- ❌ Unity/Unreal com cidade modelada: semanas de trabalho.
- ❌ SUMO/MATSim completos: curva de aprendizado alta para 1–2 dias.
- ✅ **Simulação de eventos discretos + visualização 3D no navegador**:
  1. **SimPy (Python):** 2–3 corredores reais; chegada de passageiros por hora = demanda estimada (OD 2017); ônibus chegam conforme o intervalo (headway). Mede fila e espera média.
  2. Rodar dois cenários: **antes** (intervalos atuais) × **depois** (intervalos redistribuídos, mesma frota).
  3. **deck.gl `TripsLayer` + mapa 3D com prédios extrudados (MapLibre)**, rodando no PC: bonequinhos/pontos se acumulando no ponto, ônibus passando, contadores de espera.
- Rótulo honesto na tela: "simulação ilustrativa — demanda da OD 2017, cenário simplificado".

## Por que vale
É a materialização do exemplo "ponto Y com 40 pessoas e ônibus de 30 em 30 × ponto X com 20 pessoas e ônibus de 10 em 10". Fecha o pitch e conecta MLAM (demanda) com MMC (redistribuição).

## Regra de corte
Só começar se as 3 entregas estiverem completas até **17/11**. Teto: 1 dia. Se não der, um gráfico de fila antes × depois (SimPy) já entrega 80% do impacto.
