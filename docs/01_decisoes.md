# Decisões do projeto (registro)

## D0 — Escopo
Projeto individual (Davi) cobrindo 3 disciplinas: Prompt & AI, MMC, MLAM. Recorte geográfico: **município de São Paulo**.

## D1 — Fonte de dados principal: Pesquisa OD 2017 (Metrô-SP) ✅ obtida em 09/11
- Portal oficial em manutenção → **espelho do pacote R `odbr`** (CRAN), releases do GitHub `hsvab/odbr`. Script: `scripts/baixar_od2017.py`. Citar as duas fontes no README da MLAM.
- Arquivo: `data/raw/od_sao_paulo_2017_not_harmonized.csv.gz` (separador `;`), 183.092 viagens, 128 colunas. Dicionário: `data/dicionario/od2017_dicionario_pt.csv`.
- Recorte SP→SP (`muni_o == 36` e `muni_d == 36`): **106.145 viagens na amostra ≈ 23,9 milhões de viagens/dia expandidas** (`fe_via`).
- Viagens a trabalho dentro de SP (`motivo_d` 1–3): 26.778; **52% assalariados com carteira** (`vinc1 == 1`).
- Ônibus municipal (`modoprin == 4`) para o trabalho: pico de saída **6h–7h**.

## D2 — Fontes complementares (opcionais, em ordem de prioridade)
| Fonte | Para quê | Status |
|---|---|---|
| GTFS SPTrans (`frequencies.txt` = intervalo entre ônibus por linha/faixa horária) | **oferta** atual para o comparativo demanda × oferta | a obter (cadastro em sptrans.com.br/desenvolvedores ou espelho no Mobility Database) |
| Geometria das zonas OD (`odbr::read_map`, mesmo espelho) | mapas e grafo de fluxos | a obter |
| Censo 2022 (IBGE) / RAIS (empregos por distrito e CBO) | camadas de contexto | só se sobrar tempo |

## D3 — MMC separada
A entrega de MMC usa **apenas os dados do enunciado** (4 regiões, 72 ônibus) em `entregas/mmc/`. A plataforma reaproveita a **lógica** (reconstrução + matriz de redistribuição que preserva o total) aplicada a dados reais, sem depender do enunciado.

## D4 — Documentos do RAG
Escritos por nós, **simulados**, ambientados em SP com linhas e números fictícios, marcados como simulados (não imitam publicação real). 5 documentos com 3 armadilhas (desatualização, faixa condicional, contradição) + 1 trecho de prompt injection. Ver `docs/03_ground_truth.md`.

## D5 — Chunking
Comparar A (500 caracteres, overlap 50) × B (1000, overlap 150) com o mesmo embedding e k. Decidir por qual recupera **ambos** os trechos nas perguntas armadilha; confirmar com RAGAS v1 × v2.

## D6 — GraphRAG: não
"Árvore de sim e não" = regressão logística (MLAM). "Ligar regiões" = **grafo de fluxos OD** (análise de rede), exposto ao agente como ferramenta `consultar_fluxo(origem, destino, hora)`. GraphRAG não é exigido, não pontua e é arriscado no prazo.

## D7 — Simulação 3D: opcional, só se as 3 entregas estiverem prontas até 17/11
Ver `docs/06_simulacao_3d.md`.

## D8 — Stack
Python · pandas/statsmodels/scikit-learn · NumPy · LangChain LCEL · ChromaDB · Ollama Cloud · Gradio · RAGAS · (opcional) SimPy + deck.gl. Sem React, sem API paga.
# Variáveis de entrada (OD 2017 — confirmadas no dicionário)

## Unidade de análise
Viagem com origem e destino no município de SP (`muni_o == 36 & muni_d == 36`).
Para o modelo de "quem depende do ônibus": viagens **a trabalho** (`motivo_d` ∈ {1,2,3}) de quem tem trabalho regular (`cd_ativi == 1`).
Pesos: `fe_via` (fator de expansão) para agregados populacionais; regressões na amostra (declarar).

## Alvo
| Variável | Definição | Uso |
|---|---|---|
| `usa_onibus` | 1 se `modoprin == 4` (ônibus/micro/perua do município de SP), senão 0 | regressão logística |
| `duracao` | minutos da viagem | regressão linear simples e múltipla; normal; testes de hipótese |

## Entradas (a sua ideia, traduzida em colunas)
| Ideia | Coluna | Tipo | Hipótese |
|---|---|---|---|
| CLT | `vinc1` → `clt = (vinc1 == 1)` | dummy | CLT ↑ P(ônibus) |
| Cargo na empresa | `ocup1` (11 grupos de ocupação) | categórica | ocupações operacionais ↑ P(ônibus); dirigentes ↓ |
| Setor | `setor1` (14 setores) | categórica | serviço/comércio ↑ |
| Mora longe do trabalho | `distancia` (m, linha reta) → `distancia_km` | quantitativa | ↑ distância ↑ P(transporte coletivo) até certo ponto |
| Tem carro | `qt_auto` | quantitativa | ↑ carros ↓↓ P(ônibus) |
| Renda | `renda_fa` (familiar mensal) | quantitativa | ↑ renda ↓ P(ônibus) |
| Horário de pico | `h_saida` → `pico = h_saida ∈ [6,8] ∪ [17,19]` | dummy/hora | distribuição temporal da demanda |
| Onde mora / onde trabalha | `zona_o`, `zona_d` (1–517), coords `co_o_x/y`, `co_d_x/y` | geográfica | matriz de fluxos |
| Idade | `idade` | quantitativa | controle |

⚠️ `duracao` **não** entra como preditor de `usa_onibus` (é consequência do modo — vazamento).

## Mapeamento para as exigências da MLAM
| Item | Variáveis |
|---|---|
| 02 Normal | `duracao` das viagens de ônibus a trabalho |
| 03 Testes Z (n=20 α=6% à esquerda; n=25 α=9% à direita) | `duracao`; μ₀ e σ = da população tratada; amostras com seed |
| 04 Bivariada | `duracao` ~ `distancia_km` |
| 05 Múltipla (≥3 quantitativas) | `duracao` ~ `distancia_km` + `renda_fa` + `qt_auto` (+ `idade`) |
| 06 Logística (≥3 quantitativas) | `usa_onibus` ~ `renda_fa` + `qt_auto` + `distancia_km` + `idade` (+ `clt`, `pico` como extras) |
| 07 Relatório | "Quem depende do ônibus em SP para trabalhar, e quando" |

## Do modelo ao produto
P(usa_onibus | perfil) × viagens expandidas por par de zonas e hora → **demanda estimada de ônibus por corredor/hora** → comparada à oferta (GTFS) → gap → política de redistribuição (lógica MMC).

## Tratamento planejado
1. Recorte SP→SP; 2. remover nulos em alvo e preditores; 3. `renda_fa` e `duracao` > 0; 4. outliers por IQR (registrar quantos); 5. derivar colunas; 6. exportar `entregas/mlam/dados/od2017_sp_trabalho.csv` + script que reproduz.
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
# Cronograma (meta: protótipo 18/11 · entrega 19/11 23h59)
| Data | Entrega |
|---|---|
| Seg 09 | ✅ Decisões · ✅ OD 2017 obtida · contexto do Claude montado |
| Ter 10 | MMC Etapas 1 e 2 (notebook + relatório) |
| Qua 11 | MLAM: preparação dos dados + itens 02–03 · escrever os 5 docs do RAG |
| Qui 12 | Ground truth à mão · chunking A×B · Chroma · RAG LCEL com citação |
| Sex 13 | Agente + tools (`calcular_proximo_horario`, `verificar_gratuidade`, `consultar_fluxo`) |
| Sáb 14 | MLAM 04–05 · guardrails (4) |
| Dom 15 | MLAM 06 · grafo de fluxos OD |
| Seg 16 | RAGAS v1×v2 · Gradio (Cidadão / Gestor / Dados) |
| Ter 17 | Relatório PDF MLAM · README Prompt · deploy HF Spaces · **ponto de corte da simulação 3D** |
| Qua 18 | Protótipo final · (simulação se aprovada) · vídeos (Prompt ≤3 min + pitch) |
| Qui 19 | Run all limpo · ZIP · .txt · envio |

## D9 — Atualizações de 09/11 (tarde)
- **Produto primeiro, entregas depois.** A plataforma real usa as 3 disciplinas juntas para resolver o problema. Cada entrega (MMC, MLAM, Prompt & AI) é extraída do produto e adaptada aos critérios e dados de cada enunciado. A MMC é resolvida depois com os dados do próprio enunciado, reaproveitando a lógica do produto.
- **GTFS SPTrans:** conta de desenvolvedor criada pelo Davi. Próximo passo: baixar o GTFS (routes, trips, stops, stop_times, frequencies, shapes).
- **Qualidade de dados é prioridade.** Limpeza, tratamento e engenharia de variáveis para maximizar a qualidade do modelo preditivo, sempre reproduzíveis em código (exigência da MLAM).
- **Simulação 3D** será alimentada pelos dados do próprio app: um dia "sem monitoramento" (oferta atual do GTFS × demanda OD) contra um dia "com monitoramento" (oferta redistribuída pelo modelo).
- **Passo 0 (próximo chat):** modelagem matemática do produto real + aquisição e preparo dos datasets (OD 2017 já obtida; GTFS a baixar).