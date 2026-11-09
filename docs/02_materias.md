# Matriz: o que cada matéria pede → como resolvemos

## Prompt and Artificial Intelligence (entrega 19/11 · ZIP com 7 itens)
| Critério (peso) | Pede | Como resolvemos |
|---|---|---|
| 1 Entrega (1,0) | ZIP 7 itens, Run all, vídeo ≤3 min, sem chave | checklist em `entregas/prompt_ai/README.md` |
| 2 Base/chunking (1,0) | ≥2 docs, armadilha, 2 chunkings comparados | D2 + D3 (5 docs, 3 armadilhas) |
| 3 RAG (1,5) | LCEL, Chroma c/ metadados, cita doc_id, "não sei" | retriever → prompt → ChatOllama → parser; preferir doc mais recente |
| 4 Agente (1,5) | ≥2 tools, 1 calcula, erro controlado, ≤6 chamadas | `calcular_proximo_horario(linha, hora, dia)`, `verificar_gratuidade(idade, pcd, estudante, dia)`, `consultar_status_linha(id)`; max_iterations |
| 5 Gradio (0,7) | histórico + fontes | aba Cidadão do app |
| 6 Guardrails (1,0) | 3 (trio: 4) | escopo · injection na fonte · LGPD · limite de confiança (+ teste automatizado = bônus) |
| 7 RAGAS (2,0) | 8 perguntas 4+4, ground truth próprio, explicar número | `03_ground_truth.md`; juiz e embeddings configurados explicitamente |
| 8 README (1,3) | diagrama, prints, decisões, armadilha | `entregas/prompt_ai/4_README.md` |
| Bônus | pergunta composta (2 tools), reranking medido, 4º guardrail testado | mirar a pergunta composta |

## Modelagem Matemática e Computacional (Etapas 1 e 2, 5+5 pts)
**Etapa 1 — reconstruir frota.** Variáveis N, S, L, O. Sistema:
N+S+L+O=72 · N+2S+O=76 · S+2L=52 · N+L+2O=76 → forma matricial Ax=b.
Unicidade: det(A)≠0 / posto(A)=posto([A|b])=4 (Rouché–Capelli) → solução única. Resolver com NumPy, verificar Ax=b e integralidade/não negatividade.
**Etapa 2 — redistribuir.** Necessidade = ceil(passageiros/40) por região; comparar com atual → déficit/superávit. Política: matriz T 4×4 **coluna-estocástica** (entradas ≥0, cada coluna soma 1: fração da frota de cada centro que fica/é cedida). Provar: soma(Tx)=soma(x) (1ᵀT=1ᵀ) e Tx≥0 (T≥0, x≥0). Explicar cada coeficiente. Garantir resultado inteiro. Avaliar antes × depois (ocupação, déficit).
Observação: a necessidade total coincide com a frota total — a política pode zerar o déficit (argumento forte do relatório).
Integração: vira `core/frota/` e aba Operador do app.
⚠️ Conferir com o professor se há Etapa 3 / formato do relatório (o PDF recebido termina na Etapa 2).

## MLAM (10 pts · GitHub + .txt no portal)
| Item | Pede | Com OD 2017 |
|---|---|---|
| 02 Normal (1,0) | P(X<média), P(X>mediana) + classificar evento | X = duração da viagem. P(X<μ)=0,5 por simetria; P(X>mediana) ≠0,5 se assimétrica → discutir |
| 03 Teste de hipótese (1,0) | a) unilateral à esquerda α=6%, n=20; b) à direita α=9%, n=25; σ = desvio populacional | teste Z com σ conhecido; amostras aleatórias com seed; μ₀ = média da base |
| 04 Bivariada (2,0) | dispersão, cov, Pearson, gráfico, reta, R², F, previsão | duração ~ distância |
| 05 Múltipla (2,0) | ≥3 variáveis, matrizes cov/corr, equação, R², F, previsão c/ ≥2 | duração ~ distância + renda + nº autos (+ idade) |
| 06 Logística (2,0) | equação, matriz de confusão, acurácia, classificação | usa_coletivo ~ renda + nº autos + distância |
| 07 Relatório PDF (2,0) | tabelas, gráficos, interpretação, limitações, insights | "quem depende do ônibus" → justifica Linha Certa |
| 08 Entrega | csv/xlsx + fonte, códigos com saídas, PDF, README | estrutura em `entregas/mlam/` |
Penalidades: -1 por item ausente, -2 entrega incorreta. Repositório público e acessível.

## O que você aprende (mapa)
RAG/LLMOps e avaliação (Prompt) · Álgebra linear aplicada a decisão (MMC) · Inferência e modelagem estatística com dado sujo real (MLAM) · Produto: unir tudo num pitch.
