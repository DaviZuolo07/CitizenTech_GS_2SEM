# Auditoria geral e plano até a entrega

Documento vivo. Última atualização: **quarta, 18/11/2026, 11h**. Prazo final: **19/11 às 23h59**.

Integrantes: Davi Queiroz Zuolo (RM 571669), Gustavo Zagato Bottechia (RM 569420), Daniel Vilela Mana (RM 571632). Turma 1CCPK. A GS foi dividida por disciplina; Prompt & AI, MMC e MLAM ficaram com o Davi.

## 1. Situação
| Frente | O que existe | O que falta | Estimativa |
|---|---|---|---|
| Motor de dados (produto) | pipeline OD + GTFS oficial, redistribuição, modelo preditivo, tabela das 1.310 linhas, 69 testes, notebook explicativo | nada | 100% |
| MMC | notebooks das Etapas 1 e 2 executados (reexecutados pelo Davi no Colab em 16/11), README com links do Colab | enviar; confirmar o canal com o professor | 98% |
| MLAM | base tratada, notebooks dos itens 02 a 06 rodando sozinhos no Colab, relatório PDF (item 07), README, `.txt` do Portal pronto | commit e push; ler o relatório PDF; enviar o `.txt` | 98% |
| Prompt & AI | notebook completo (seções 0 a 8) revisado em 16/11 (D21), base, ferramentas, guardrails, README, 8 respostas de referência | **fechar a execução real** (seções 0 a 6 já passaram na Groq; a 7 nunca terminou); prints; vídeo; completar os arquivos 5 e 7; ZIP | 80% |
| Simulação 3D | pronta: `simulacao/linha_certa_simulacao.html` | nada obrigatório | 100% |
| App Gradio (abas Gestor e Dados) e deploy | só a aba Cidadão, dentro do notebook | abas Gestor e Dados; Hugging Face Spaces | 20% |
| Pitch | roteiro, números medidos, simulação | gravar o vídeo | 40% |

**Dá tempo?** As três entregas, sim. O notebook de Prompt & AI já rodou duas vezes no Colab (13 e 14/11) e as falhas das duas execuções estão corrigidas; falta a execução que fecha a seção 7, com as chaves da Groq e do Google AI Studio (a Cerebras deixou de ser gratuita em 14/11). Em 16/11 a folga até o prazo é de três dias. O que está em risco é o app com três abas publicado no Hugging Face; ele não vale nota em nenhuma disciplina e deve ser o primeiro corte. O pitch se sustenta com a simulação, os gráficos do notebook explicativo e a aba Cidadão.

## 2. O que mudou em 12/11
### Ollama deixou de ser gratuito (aviso do professor em 11/11)
- O notebook passou a usar `ChatOpenAI` contra provedores com API compatível com OpenAI, da lista do laboratório do professor: Groq, Cerebras, Hugging Face, Google AI Studio, Mistral, OpenRouter e NVIDIA NIM.
- **Detecção automática:** usa o primeiro provedor cuja chave estiver nos Secrets do Colab. Basta cadastrar uma chave.
- **Embeddings sem chave:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, rodando no próprio Colab. Não gasta cota e entende português.
- O juiz do RAGAS é o mesmo modelo, passado explicitamente; `max_workers=1` e novas tentativas automáticas para respeitar o limite de uso dos planos gratuitos.
- Validação: todas as células executadas com modelo e embeddings falsos, inclusive a detecção do provedor. **A execução real continua pendente.**

### Textos de análise passam a ser gerados com os números medidos
- **Justificativa do chunking, leitura dos números do RAGAS e conclusão** agora são montadas pelo código a partir dos resultados da execução (qual versão venceu em cada métrica, simples × armadilha, pior pergunta, documento que faltou no contexto, melhoria proposta). Nenhum número é digitado.
- **Divisão de tarefas** preenchida: a entrega de Prompt & AI foi feita pelo Davi.

### Linhas reais de São Paulo
- `data/processed/linhas_onibus.csv`: uma linha por sentido de cada linha de ônibus, com trajeto (de onde até onde), destino, extensão, partidas por dia e frota estimada às 6h, às 17h e no máximo.
- Totais do GTFS: **1.309 linhas, 2.236 sentidos, 34.341 km de trajetos, 165.105 partidas por dia útil**. A maior é a 6000-10 (Term. Parelheiros – Term. Sto. Amaro), com cerca de 50 ônibus às 6h.
- A fonte dos trajetos é o próprio GTFS da SPTrans (`shapes.txt` traz a geometria de cada trajeto; `stops.txt`, as 22 mil paradas). São Paulo já está mapeada no motor: cada parada é atribuída a uma zona, distrito, subprefeitura e região. A API Olho Vivo acrescentaria a posição dos ônibus em tempo real e fica como evolução.

### Simulação 3D
- Arquivo único, abre com dois cliques, sem internet. Mostra a mesma cidade fictícia duas vezes, lado a lado: frota fixa × frota redistribuída a cada hora.
- **O modelo está dentro:** a probabilidade de usar ônibus de cada bairro vem dos coeficientes da regressão logística treinada na OD 2017; a forma do dia vem dos embarques reais por hora; a redistribuição é a regra do produto, reescrita em JavaScript e conferida contra o Python (mesmos resultados no caso da MMC e no teste do piso).
- Resultado desta cidade: espera média de 11,1 para 6,8 min (−38%), maior fila de 219 para 90 pessoas, mesma quilometragem. Sem redistribuir, seriam necessários 8 ônibus a mais (44 em vez de 36) para a mesma espera.
- **Limite:** é uma demonstração numa cidade pequena e controlada. Não valida o ganho em São Paulo; os números da cidade real são os do motor (seção 5).

## 3. Decisões de 12/11 (D14)
| Decisão | Motivo |
|---|---|
| Provedor detectado pelos Secrets, em vez de um fixo | cada aluno cria a própria chave; o notebook roda com qualquer uma da lista do professor |
| Embeddings locais, não por API | sem chave, sem limite de uso, resultado reproduzível |
| Análises escritas pelo código com os valores da execução | o enunciado proíbe número estimado; assim o texto sempre corresponde ao que foi medido |
| ~~**Ground truth continua em branco no notebook**~~ — **revertida pela D16 em 13/11** | era: o enunciado limita o critério 7 (2 pontos) a 1,0 se a resposta de referência for gerada por IA. A D16 registra a decisão do Davi de redigir as 8 respostas com apoio de IA e conferi-las, aceitando essa perda; as declarações do notebook, da certificação e do chat log dizem exatamente isso |
| **Base documental continua simulada e em `.md`** | o enunciado exige base "simulada, escrita pelo grupo", em `.txt` ou `.md`, e desconta autoria por "texto de fonte pública identificável". Trocar por PDFs reais perderia ponto nos critérios 2 e 7. Regras reais entram no pitch como evolução do produto |
| Simulação em cidade fictícia pequena, não em São Paulo inteira | pedido do Davi; cabe na tela e roda em qualquer computador. O ganho em São Paulo é medido pelo motor, não pela simulação |
| Economia expressa em "ônibus equivalentes", com custo por km como parâmetro | com frota fixa, a quilometragem não muda; a economia real é a frota que deixaria de ser necessária. O valor em reais é ilustrativo e está rotulado assim |

## 4. Como cada disciplina é entregue
### MMC
- **O que vai:** `entregas/mmc/01_etapa1_reconstrucao.ipynb` e `02_etapa2_redistribuicao.ipynb` (já com saídas e integrantes).
- **Como:** pelo canal indicado pelo professor (confirmar se é o Portal e se ele quer PDF; se quiser, exportar cada notebook em PDF pelo menu Arquivo → Imprimir).
- O projeto tem só as Etapas 1 e 2.

### MLAM
- **O que vai no Portal:** um único arquivo `.txt` com nome completo e RM dos três e o link do GitHub.
- **Link sugerido:** `https://github.com/DaviZuolo07/CitizenTech_GS_2SEM/tree/main/entregas/mlam` (a pasta tem a base, os três notebooks, o README e, quando pronto, o PDF).
- **Antes de enviar:** relatório PDF dentro de `entregas/mlam/relatorio/`; repositório público (já está) e com o último push.
- Erro de entrega custa 2 pontos; item ausente, 1 ponto.

### Prompt & AI
- **O que vai no Portal:** `GS2026_2_1CCPK_<NOME_DO_GRUPO>.zip` com exatamente:
  1. `1_Notebook_GS2026_2.ipynb` (executado, com saídas)
  2. `2_base_documental/` (os 5 documentos e a pasta `dados_ferramentas/`)
  3. `3_avaliacao_ragas.json` (gerado pelo notebook)
  4. `4_README.md` (com prints e números)
  5. `5_certificacao.txt` (tela final, links, nomes e RMs)
  6. `6_Chat_Log.txt` (registro do uso de IA)
  7. `7_demo_video_url.txt` (link do vídeo no YouTube, não listado, até 3 min, com cada integrante se apresentando no início)
- **Nunca** deixar chave no notebook, nos prints ou no ZIP.

### Pitch geral (top 3)
Vídeo de até 3 minutos, sem divisão por disciplina:
| Tempo | O que aparece | Fonte |
|---|---|---|
| 0:00–0:20 | a dor: fila no ponto de um bairro, ônibus vazio em outro | simulação, lado "sem" |
| 0:20–0:50 | o dado real: 9,7 milhões de embarques por dia; às 17h a ocupação vai de 0,20 a 0,80 entre subprefeituras | notebook explicativo, seção 6 |
| 0:50–1:30 | o gestor: redistribuir 1.193 ônibus (9% da frota) leva a faixa para 0,25–0,56, sem comprar veículo e sem tirar mais de 20% de nenhuma área | motor de dados |
| 1:30–2:10 | a simulação lado a lado, em 8×, até o placar final | `simulacao/` |
| 2:10–2:40 | o cidadão: pergunta-armadilha respondida com fonte; tentativa de injection recusada | notebook de Prompt & AI |
| 2:40–3:00 | custo próximo de zero, o que é medido e o próximo passo (Olho Vivo) | — |

O que o pitch não pode afirmar: fim da superlotação (o modelo mede ocupação média, não o trecho mais cheio); economia em reais como fato; que a simulação prova o resultado em São Paulo.

## 5. Números do motor (cidade real, medidos)
- 9,72 milhões de embarques de ônibus por dia na OD 2017; contar só o "modo principal" esconderia 43% deles.
- 17h: ocupação média de 0,20 (Perus-Anhanguera) a 0,80 (Pinheiros, Butantã). Realocando 1.193 ônibus, a faixa vai para 0,25–0,56.
- Espera média ponderada às 17h: de 8,69 para 8,37 min. Às 6h ela sobe 0,25 min: igualar lotação e reduzir espera são objetivos diferentes.
- Modelo preditivo: AUC 0,81 no completo e 0,71 no de 4 variáveis; a distância é a entrada que mais pesa; cada carro corta a chance de usar ônibus pela metade.
- Viagem de ônibus ao trabalho: 58 min em média, contra 39 min na média de todos os modos.

## 6. Etapas até a entrega
| # | Etapa | Estado | Quem |
|---|---|---|---|
| 1 | Motor de dados e documentação | feito | — |
| 2 | Entrega MMC | feito | — |
| 3 | Entrega MLAM: notebooks e base | feito | — |
| 4 | Prompt & AI: base, ferramentas, notebook, README | feito | — |
| 5 | Prompt & AI nos provedores novos | feito em 12/11 | — |
| 6 | Linhas reais de São Paulo | feito em 12/11 | — |
| 7 | Simulação 3D | feito em 12/11 | — |
| 8 | Primeira execução real no Colab (seções 0 a 6) | feito em 13/11 | — |
| 9 | Correções que a execução real mostrar | feito em 13 e 14/11 (D17) | — |
| 10 | 8 respostas de referência (D16: IA redige, Davi confere) | feito em 13/11 | Davi valida |
| 11 | RAGAS medido e JSON exportado | **pendente** — chaves da Groq e do Google | Davi roda |
| 12 | Relatório PDF da MLAM | feito em 12/11 | Davi lê e valida |
| 13 | Prints no README de Prompt & AI | pendente | Davi |
| 14 | Vídeo de Prompt & AI e vídeo do pitch | pendente | grupo |
| 15 | ZIP, `.txt` e envios | pendente | Davi |
| 16 | App com abas Gestor e Dados; deploy | opcional | só se sobrar tempo |

### Calendário
| Dia | Trabalho |
|---|---|
| Qui 12 | ✅ provedores, simulação, linhas · Davi: commit e push, criar a chave, rodar o Colab |
| Sex 13 | correções do Colab · 8 respostas de referência · RAGAS · relatório PDF da MLAM |
| Sáb 14 | ✅ correções do RAGAS (D17) · Davi: chave da Cerebras, rodar o Colab inteiro · prints e README de Prompt & AI |
| Dom 15 | vídeo de Prompt & AI · roteiro final do pitch |
| Seg 16 | vídeo do pitch · conferência dos três pacotes |
| Ter 17 | `Run all` limpo no Colab · montar o ZIP · reserva |
| Qua 18 | protótipo final · reserva |
| Qui 19 | envios, de preferência pela manhã |

## 7. O que só o grupo pode fazer
1. **Commit e push** (o notebook baixa a base do GitHub).
2. **Cadastrar duas chaves gratuitas** nos Secrets do Colab, com "Notebook access": `GROQ_API_KEY` (agente) e `GOOGLE_API_KEY` (juiz do RAGAS). A Cerebras e a Hugging Face deixaram de ter plano gratuito utilizável.
3. **Rodar o notebook no Colab** e enviar qualquer erro.
4. **Validar as 8 respostas de referência** da seção 7 do notebook, conferindo cada uma contra os documentos que ela cita (D16).
5. **Ler e revisar os 5 documentos** da base e registrar o uso de IA no `6_Chat_Log.txt`.
6. **Prints, vídeos, `5_certificacao.txt` e `7_demo_video_url.txt`.**
7. **Confirmar com o professor de MMC** o canal de envio.

## 8. Riscos abertos
| Risco | Efeito | O que fazer |
|---|---|---|
| ~~Notebook nunca rodou com modelo real~~ | **resolvido**: rodou em 13 e 14/11 | as falhas das duas execuções estão corrigidas na D17 |
| Modelo pequeno não segue o formato do agente | o agente gasta voltas e pode não chegar à resposta | resolvido na D15: cada candidato passa por um teste de formato antes de ser usado |
| ~~Limite de uso do plano gratuito no RAGAS~~ | **ocorreu em 13/11** | resolvido na D17: `bypass_n=True`, juiz em outra chave, `max_tokens=800`. O texto de análise continua avisando quando o juiz falha |
| Acurácia do item 06 da MLAM abaixo do chute da maioria no limiar escolhido | pergunta na correção | já explicado no notebook; a tabela mostra também o limiar 0,5 |
| Nenhuma chave com folga de tokens para o juiz do RAGAS | métricas vazias e critério 5 (2 pontos) sem medição | cadastrar a chave do Google AI Studio além da Groq. Sem a segunda chave o notebook usa a cota do agente, avisa na saída e retoma do cache na execução seguinte |

## 9. Atualização de 12/11, 17h
- **GTFS oficial instalado** (versão 12/11/2026 da SPTrans). O pipeline e o notebook explicativo foram executados de novo. Os resultados quase não mudam: às 17h, frota de 13.317 (antes 13.320), 1.192 ônibus realocados (antes 1.193), ocupação de 0,80 para 0,56, espera de 8,70 para 8,38 min. O feed novo tem 1.310 linhas e 34.353 km de trajetos. Os números citados nas seções anteriores e em `docs/08` são os do feed de 09/11; a diferença é de arredondamento.
- **Relatório estatístico da MLAM pronto:** `entregas/mlam/relatorio/relatorio_estatistico.pdf` (5 páginas), com a fonte em `.html` e as figuras na mesma pasta. Todos os números vêm dos notebooks 01 a 03.
- **`6_Chat_Log.txt` e `5_certificacao.txt` preenchidos** em rascunho. No chat log falta a parte "o que eu verifiquei"; na certificação, o link do vídeo e a tela final.
- **Respostas de referência:** ficam na seção 7 do notebook, na lista `AVALIACAO`. Em 13/11 foram preenchidas (D16).

## 10. Atualização de 13 e 14/11 — as três falhas da seção 7 e a troca de provedor

As seções 0 a 6 passaram na primeira execução real. A seção 7 (RAGAS) foi a única que falhou, e trouxe **três erros de causas diferentes na mesma saída**, o que à primeira vista parecia um problema só. Todos registrados na **D17**:

| Erro | Causa | Correção |
|---|---|---|
| `400 'n' : number must be at most 1` (jobs 1, 5, 9, 13…) | o RAGAS 0.4 pede `n>1` ao juiz: ele gera várias opiniões e tira a maioria. Groq e Cerebras recusam esse parâmetro | `LangchainLLMWrapper(..., bypass_n=True)` — correção oficial (issue #2354 do RAGAS). Conferido que o parâmetro existe no `ragas==0.4.3`, a versão fixada na célula 1 |
| `429 tokens per day (TPD): Limit 200000` (a maioria dos jobs) | o RAGAS gasta ~150 mil tokens por execução (8 perguntas × 2 estratégias × 4 métricas = 64 jobs). Somado ao gasto do agente, estourava a cota diária da Groq | o juiz passou a usar **outra chave**, de outro provedor, para que as duas cotas não se somem |
| `429 OTPM: Limit 1000, Requested 1207` e `LLMDidNotFinishException` | `max_tokens=1500` no juiz passava do limite de tokens de saída por minuto do plano gratuito | `max_tokens=800` no juiz |

### O 403 da Hugging Face (14/11) não era o modelo
A tentativa de pôr o juiz na Hugging Face falhou antes de qualquer modelo responder: `403 does not have sufficient permissions to call Inference Providers` nos **três** candidatos (`Qwen2.5-72B`, `Llama-3.3-70B` e `gpt-oss-120b`). Falhar igual nos três é o sinal de que a causa não é o modelo, é o token. A Hugging Face exige token *fine-grained* com "Make calls to Inference Providers" marcado — e, mais a fundo, **o plano gratuito deixou de incluir crédito para esses provedores** (free = US$ 0,00/mês; só conta PRO recebe crédito). Trocar para um modelo menor, como o Llama 3.1 8B, daria exatamente o mesmo 403.

Por isso a Hugging Face foi para o **fim** da lista de provedores, com o motivo escrito em comentário, e a mensagem de erro do notebook passou a reconhecer esse 403 e a apontar a Cerebras como caminho.

### O que o notebook faz agora
- **`PROVEDORES` ordenado pela folga de tokens por dia** do plano gratuito: Cerebras (1 mi/dia), Groq (200 mil/dia), Google AI Studio, Mistral, OpenRouter, NVIDIA e, por último, Hugging Face.
- **A escolha do juiz é separada da do agente.** O notebook percorre a lista de preferência em duas passadas: primeiro procura um provedor **diferente** do agente, e só depois aceita o mesmo. Quando cai na mesma cota, imprime um aviso em vez de falhar em silêncio.
- **Nenhum modelo de 8B na preferência do juiz.** As 4 métricas dependem de o juiz devolver JSON válido; modelos pequenos erram o formato e a métrica volta vazia (NaN), o que registraria "o juiz falhou" em vez de uma medição. A preferência só tem modelos de 70B ou mais: `gpt-oss-120b` e `qwen-3-235b` na Cerebras, `llama-3.3-70b-versatile` na Groq, `gemini-2.5-flash` no Google. Para o **agente** um modelo menor serve, porque ali só é preciso acertar o formato ReAct em texto (D15).
- A lógica de escolha foi conferida em seis cenários de chave: só Groq, Groq + Cerebras, só Cerebras, Groq + HF com o 403, Cerebras recusando o `gpt-oss-120b`, e um provedor sem juiz preferido.

### O que falta do lado do Davi (substituído pela seção 11)
1. ~~Criar a chave em `cloud.cerebras.ai`~~ (a Cerebras passou a exigir crédito; ver seção 11)
2. Commit e push (o notebook baixa a base documental do GitHub).
3. Rodar o notebook inteiro e conferir que a seção 7 imprime as 4 métricas nas duas estratégias.

## 11. Revisão geral das entregas em 16/11 (D20 e D21)
Pedido do Davi: revisar as três entregas contra os enunciados, corrigir o que houver e dar nota a cada uma.

**MLAM.** Corrigido o `FileNotFoundError` do Colab (o `02` e o `03` baixam a base do repositório quando abertos sozinhos; testado numa pasta vazia). Encontrado e corrigido um problema de reprodutibilidade: a divisão treino/teste dependia da versão do scikit-learn; agora é uma função fixa do código da família, e o relatório PDF, a figura 4 e o README foram atualizados para os números novos do item 06 (AUC 0,700; conclusões inalteradas). Interpretações com os valores medidos acrescentadas ao `03`. Criado `entregas/mlam/ENTREGA_PORTAL_MLAM.txt`, pronto para o Portal.

**MMC.** Sem alteração de conteúdo: todos os itens (a–f das duas etapas) presentes, com saídas; a expansão de Laplace do determinante foi conferida à mão. README com links do Colab. O enunciado não diz como entregar: confirmar o canal com o professor.

**Prompt & AI.** Célula de configuração reescrita (D21): agente na Groq, juiz no Google, catálogo do Google normalizado, Gemini sem "pensamento", 8 chamadas por minuto. Conclusão com o diagrama do fluxo e as decisões (exigência da seção 7 do briefing). README e chat log atualizados. Verificado que não há chave de API em nenhum arquivo rastreado nem no histórico do git. **Continua sem execução real completa**: a seção 7 nunca terminou no Colab.

### O que só o Davi pode fazer, em ordem
1. Commit e push (os notebooks baixam a base do GitHub; sem push o professor recebe a versão antiga).
2. Cadastrar `GROQ_API_KEY` e `GOOGLE_API_KEY` nos Secrets e rodar o notebook de Prompt & AI inteiro (cerca de 25 minutos).
3. Reescrever com as próprias palavras as 8 respostas de referência, lendo os documentos, para poder declarar autoria do grupo (ver nota do critério 7).
4. Baixar o notebook executado e o `3_avaliacao_ragas.json`; prints e números no `4_README.md`; vídeo; completar os arquivos 5, 6 e 7; montar o ZIP.
5. Enviar: `.txt` da MLAM no Portal, ZIP de Prompt & AI no Portal, MMC pelo canal do professor.

## 12. Revisão de 17/11 (execução real do RAGAS)
**Resultado da execução de 16/11:** notebook rodou inteiro, 0 erros, `3_avaliacao_ragas.json` exportado no Colab. Problemas: juiz = próprio agente (Google 404 nos Gemini 2.5 para chave nova), 8 de 64 medições vazias por cota da Groq, texto de diagnóstico contraditório. Corrigido no notebook (D22). As médias de 16/11 (v2: faithfulness 0,94, answer_relevancy 0,64, context_precision 0,57, context_recall 0,83) deixam de valer se o notebook rodar de novo.

**Ground truth (critério 7):** o texto das 8 respostas de referência no notebook é idêntico ao rascunho que a IA escreveu em 13/11. As declarações (notebook, 5 e 6) dizem "redigidas com apoio de IA e conferidas pelo grupo", e isso continua correto enquanto o texto for o da IA. Para declarar autoria própria, o grupo precisa reescrever as respostas com as próprias palavras antes de rodar.

**Pendências do Davi, em ordem:** (1) opcional: reescrever as 8 respostas; (2) commit e push; (3) Colab: Ambiente de execução → Desconectar e excluir ambiente → Executar tudo, com GROQ_API_KEY e GOOGLE_API_KEY; (4) baixar o `.ipynb` executado e o `3_avaliacao_ragas.json` do painel Arquivos; (5) prints 1–10 em `entregas/prompt_ai/prints/`; (6) RAGAS e frase do chunking no README; (7) arquivos 5, 6 e 7; (8) vídeo ≤ 3 min, YouTube não listado, cada integrante se apresenta; (9) ZIP `GS2026_2_1CCPK_<GRUPO>.zip`; (10) envios: ZIP de Prompt & AI e `.txt` da MLAM no Portal, MMC pelo canal do professor.


## 13. Execução final de 17/11 (tarde)
**Resultado:** notebook rodou inteiro no Colab, 0 erros; juiz `gemini-3.1-flash-lite` (Google), separado do agente (`qwen/qwen3.8-27b`, Groq); 64 de 64 medições. v2 (chunking B) vence nas 4 métricas: faithfulness 0,875, answer_relevancy 0,691, context_precision 0,615, context_recall 0,750 (v1: 0,815 / 0,643 / 0,437 / 0,542). Armadilhas na v2: context_recall 1,00 (v1: 0,33). Pior pergunta: primeira partida da 502C-10 (recall 0 nas duas versões) → busca híbrida BM25 + reranking. Ficaram na meta faithfulness e context_recall.

**Feito pela IA (D23):** correção da frase "simples × armadilha" (células 27 e 29); 9 prints em `entregas/prompt_ai/prints/`; README com tabelas, leitura e análise; `5_certificacao.txt` com a tela final; `6_Chat_Log.txt` com a verificação; `montar_zip.py`, que recusa montar se faltar algo.

**Falta (Davi):** (1) no Colab, colar as células 27 e 29 corrigidas, rodar 27–29, baixar o `.ipynb` e o `3_avaliacao_ragas.json` (pasta `content`) para `entregas/prompt_ai/`; (2) print do Gradio `prints/05_gradio.png`; (3) vídeo ≤ 3 min, link nos arquivos 5 e 7; (4) `python montar_zip.py`; (5) commit e push; (6) envios no Portal (ZIP de Prompt & AI e `.txt` da MLAM) e MMC pelo canal do professor.

## 14. Execução de 18/11 e o defeito do índice duplicado
A execução da manhã de 18/11 saiu pior que a de 17/11 e a causa não era o modelo: a coleção do ChromaDB tinha sido preenchida duas vezes no mesmo kernel (24 chunks em vez de 12). Com trechos repetidos ocupando o `k`, a seção 3 respondeu **errado** a armadilha do domingo. Corrigido na D24: a indexação apaga a coleção antes de recriar e confere o total.

Também ficou claro que a correção da D23 (frase "simples × armadilha") não estava na cópia do Colab: o notebook rodado era anterior ao patch. As duas correções estão agora no `.ipynb` do repositório.

**Estado:** notebook corrigido e pronto para a execução final; prints 1–4 e 6–10 de 17/11 (as saídas não mudam de forma relevante, mas o 01, o 03 e o 10 valem regerar depois da execução final); README e certificação passam a ser preenchidos por `atualizar_entrega.py`; chat log reescrito com as decisões do grupo e a auditoria do ground truth; vídeo gravado, falta o áudio.

**Ordem até a entrega:** (1) Colab: *Desconectar e excluir ambiente* → *Executar tudo*, com o notebook do repositório; (2) baixar o `.ipynb` e o `3_avaliacao_ragas.json` para `entregas/prompt_ai/`; (3) `python atualizar_entrega.py`; (4) link do vídeo nos arquivos 5 e 7; (5) `python montar_zip.py`; (6) commit e push; (7) envios.
