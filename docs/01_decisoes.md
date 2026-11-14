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

## D10 — Modelo do produto implementado (10/11)
Decisões aprovadas e ajustes impostos pelos dados (demanda por trecho de ônibus, carga repartida pelo trajeto, fluxos em subprefeitura × faixa do dia, piso de cobertura de 20%), resultados e limitações: ver `docs/08_modelo_produto.md`. Onde houver conflito com a D9, vale a D10.

## D11 — Entregas de MMC e MLAM extraídas (11/11)
Notebooks de entrega autossuficientes em `entregas/mmc/` e `entregas/mlam/`; desenho dos testes de hipótese (referência = todos os trabalhadores; amostras de carro e de ônibus); MMC sem piso de cobertura; Olho Vivo fora do MVP. Auditoria, o que falta por disciplina, peso de cada entrada do modelo e cronograma revisto: ver `docs/09_auditoria_e_plano.md`.

## D12 — Base documental e ferramentas do agente (11/11, tarde)
- 5 documentos simulados em `base_documental/`, com 3 linhas fictícias (714A-10, 502C-10, 318N-10) e o Terminal Ipê Roxo. Armadilhas: desatualização (doc_02 × doc_03), faixa condicional (doc_04), contradição (doc_01 × doc_05) e prompt injection no doc_05.
- Ferramentas em `core/agent/ferramentas.py`, funções puras e testadas: `calcular_proximo_horario`, `verificar_gratuidade`, `consultar_fluxo`. Leem `operacao_vigente.json` (tabela já com a portaria), para que RAG e ferramenta não se contradigam.
- Entregas passam a levar os três integrantes; Prompt & AI no escopo de trio (8 perguntas, 4 guardrails).
- MMC: só Etapas 1 e 2; a nota sobre "Etapa 3" foi removida de `docs/02_materias.md`.
- O GTFS em `data/raw/` continua sendo a cópia de 10/11; o oficial ainda precisa ser copiado para lá.

## D13 — Notebook de Prompt & AI montado (11/11)
- Padrão copiado das aulas do Prof. Jorge: `OLLAMA_HOST=https://ollama.com`, `ChatOllama("qwen3.6:27b", temperature=0)`, `OllamaEmbeddings("nomic-embed-text")`, agente `create_react_agent` + `AgentExecutor`, RAGAS com juiz e embeddings explícitos.
- Versões travadas e testadas em conjunto (langchain 0.3.27 etc.). O `AgentExecutor` das aulas não existe no langchain 1.x, por isso o pin em 0.3.
- Ferramentas com entrada em um único texto ("linha, hora, dia"), porque o ReAct passa só um `Action Input`.
- Prompt ReAct local (sem `hub.pull`), para o notebook não depender do LangChain Hub.
- Guardrails ligados por duas listas de checagens (entrada e saída): a seção 5 (interface) define o fluxo e a seção 6 registra os guardrails, mantendo a ordem de seções exigida.
- Limite de confiança determinístico: a resposta só passa se citar um documento realmente consultado ou vier de ferramenta de cálculo.
- Base e dados das ferramentas em `entregas/prompt_ai/2_base_documental/`; no Colab o notebook baixa do repositório público.
- Validação feita: todas as células executadas com modelo e embeddings falsos (sem rede), incluindo agente, guardrails, Gradio e a chamada do RAGAS. **Falta a execução real no Colab**, que depende da chave.
- Ground truth das 8 perguntas em branco: o notebook para na seção 7 até o grupo escrevê-las.

## D14 — Provedores novos, linhas reais e simulação 3D (12/11)
- Ollama Cloud deixou de ser gratuito: o notebook de Prompt & AI usa `ChatOpenAI` com o primeiro provedor da lista do professor cuja chave estiver nos Secrets; embeddings locais (sentence-transformers).
- Justificativa do chunking, leitura do RAGAS e conclusão são montadas pelo código com os valores medidos.
- Ground truth continua em branco e a base continua simulada em `.md`: as duas coisas são exigências do enunciado (critérios 2 e 7).
- `data/processed/linhas_onibus.csv`: as 1.309 linhas de ônibus do GTFS, com trajeto, extensão e frota estimada.
- `simulacao/linha_certa_simulacao.html`: cidade fictícia em 3D, sem × com Linha Certa, usando os coeficientes do modelo e a regra de redistribuição do produto. Supera a D7 (a simulação foi feita antes do corte de 17/11, a pedido do Davi).
- Detalhes, forma de entrega de cada disciplina, roteiro do pitch e calendário: `docs/09_auditoria_e_plano.md`.

## D15 — Escolha do modelo por teste de formato (12/11)
Na primeira execução real (Groq, `openai/gpt-oss-20b`), o RAG funcionou e o agente falhou com "Tool choice is none, but model called a tool": o modelo tenta uma chamada de ferramenta nativa ao ver o formato ReAct em texto, e a Groq recusa porque nenhuma ferramenta foi declarada na requisição. Correção: cada provedor tem uma lista de modelos candidatos, e o notebook usa o primeiro que passa num teste curto no formato do agente. Na Groq a ordem é Llama 3.3 70B, Qwen 3.8 27B, Llama 3.1 8B e, por último, gpt-oss.

## D16 — Ground truth das 8 perguntas redigida com apoio de IA (13/11)
Decisão do Davi, registrada como tal: as 8 respostas de referência do RAGAS foram redigidas a partir dos documentos da base e conferidas por ele, em vez de escritas à mão desde o início. O enunciado limita o critério 7 a 1,0 de 2,0 quando a ground truth é gerada por IA, e essa perda está aceita. As declarações do notebook, do `5_certificacao.txt` e do `6_Chat_Log.txt` dizem exatamente isso — a alternativa seria declarar autoria que não houve.

## D17 — Juiz do RAGAS em provedor separado do agente (14/11)
A execução de 13/11 falhou nos 64 jobs do RAGAS com três erros distintos, e cada um exigiu uma correção diferente:

| Erro observado | Causa | Correção |
|---|---|---|
| `400 'n' : number must be at most 1` nos jobs ímpares | o RAGAS 0.4 pede `n>1` ao juiz (gera várias opiniões e tira a maioria); Groq e Cerebras recusam esse parâmetro | `LangchainLLMWrapper(..., bypass_n=True)` — correção oficial, issue #2354; confirmado presente no `ragas==0.4.3` |
| `429 tokens per day (TPD): Limit 200000` na maioria dos jobs | o RAGAS gasta ~150 mil tokens por execução (8 perguntas × 2 estratégias × 4 métricas); somado ao gasto do agente, estoura o limite diário do plano gratuito da Groq | juiz passa a usar **outra chave**, para que as duas cotas não se somem |
| `429 OTPM: Limit 1000, Requested 1207` e `LLMDidNotFinishException` | `max_tokens=1500` no juiz passava do limite de tokens de saída por minuto | `max_tokens=800` no juiz |

**Ordem dos provedores trocada.** A lista `PROVEDORES` passou a ser ordenada pela folga de tokens por dia do plano gratuito: Cerebras (1 milhão/dia) na frente, Groq (200 mil/dia) em segundo. A Hugging Face foi para o **fim** da lista: desde 2026 o plano gratuito não inclui crédito para os Inference Providers (free = US$ 0,00/mês) e o token precisa ser *fine-grained* com "Make calls to Inference Providers" marcado — sem isso a API responde `403 does not have sufficient permissions`, que foi o erro de 14/11. Ela só serve com conta PRO.

**Por que nenhum modelo de 8B no juiz.** As 4 métricas dependem de o juiz devolver JSON válido. Modelos pequenos erram o formato e a métrica volta vazia (NaN), o que registraria "o juiz falhou" em vez de uma medição. A lista de preferência do juiz só tem modelos de 70B ou mais: `gpt-oss-120b` e `qwen-3-235b` na Cerebras, `llama-3.3-70b-versatile` na Groq, `gemini-2.5-flash` no Google. Para o **agente** um modelo menor serve, porque ele só precisa acertar o formato ReAct em texto (D15).

A escolha do juiz é automática: o notebook percorre a preferência em duas passadas, primeiro procurando um provedor diferente do agente e só depois aceitando o mesmo, e avisa na saída quando caiu na mesma cota. Lógica conferida em seis cenários de chave (só Groq, Groq + Cerebras, só Cerebras, Groq + HF com 403, Cerebras recusando o 120b, e um provedor sem juiz preferido).
