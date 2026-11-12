# Auditoria geral e plano até a entrega

Documento vivo. Última atualização: **quinta, 12/11/2026, 16h30**. Prazo final: **19/11 às 23h59**. Protótipo: 18/11.

Integrantes: Davi Queiroz Zuolo (RM 571669), Gustavo Zagato Bottechia (RM 569420), Daniel Vilela Mana (RM 571632). Turma 1CCPK. A GS foi dividida por disciplina; Prompt & AI, MMC e MLAM ficaram com o Davi.

## 1. Situação
| Frente | O que existe | O que falta | Estimativa |
|---|---|---|---|
| Motor de dados (produto) | pipeline OD + GTFS, redistribuição, modelo preditivo, tabela das 1.309 linhas, 69 testes, notebook explicativo | GTFS oficial no lugar da cópia | 95% |
| MMC | notebooks das Etapas 1 e 2 executados, README | enviar | 95% |
| MLAM | base tratada, notebooks dos itens 02 a 06, README | **relatório PDF (item 07, 2 pontos)**; `.txt` do portal | 75% |
| Prompt & AI | notebook completo (seções 0 a 8) já nos provedores novos, base, ferramentas, guardrails, README | **primeira execução real no Colab**; 8 respostas de referência; prints; vídeo; arquivos 5, 6 e 7; ZIP | 65% |
| Simulação 3D | pronta: `simulacao/linha_certa_simulacao.html` | nada obrigatório | 100% |
| App Gradio (abas Gestor e Dados) e deploy | só a aba Cidadão, dentro do notebook | abas Gestor e Dados; Hugging Face Spaces | 20% |
| Pitch | roteiro, números medidos, simulação | gravar o vídeo | 40% |

**Dá tempo?** As três entregas, sim, com uma condição: o notebook de Prompt & AI precisa rodar no Colab **até sexta, 13/11**, para sobrar tempo de corrigir o que a execução real mostrar. O que está em risco é o app com três abas publicado no Hugging Face; ele não vale nota em nenhuma disciplina e deve ser o primeiro corte. O pitch se sustenta com a simulação, os gráficos do notebook explicativo e a aba Cidadão.

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
| **Ground truth continua em branco no notebook** | o enunciado zera quase todo o critério 7 (2 pontos) se a resposta de referência for gerada por IA, e a instrução do próprio Projeto proíbe. O notebook indica, para cada pergunta, quais documentos ler |
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
| 8 | Primeira execução real no Colab (seções 0 a 6) | **pendente** | Davi |
| 9 | Correções que a execução real mostrar | pendente | depois da 8 |
| 10 | 8 respostas de referência, à mão | **pendente** | Davi |
| 11 | RAGAS medido e JSON exportado | pendente | Davi roda |
| 12 | Relatório PDF da MLAM | **pendente** | próximo passo |
| 13 | Prints no README de Prompt & AI | pendente | Davi |
| 14 | Vídeo de Prompt & AI e vídeo do pitch | pendente | grupo |
| 15 | ZIP, `.txt` e envios | pendente | Davi |
| 16 | App com abas Gestor e Dados; deploy | opcional | só se sobrar tempo |

### Calendário
| Dia | Trabalho |
|---|---|
| Qui 12 | ✅ provedores, simulação, linhas · Davi: commit e push, criar a chave, rodar o Colab |
| Sex 13 | correções do Colab · 8 respostas de referência · RAGAS · relatório PDF da MLAM |
| Sáb 14 | prints e README de Prompt & AI · revisão do relatório da MLAM |
| Dom 15 | vídeo de Prompt & AI · roteiro final do pitch |
| Seg 16 | vídeo do pitch · conferência dos três pacotes |
| Ter 17 | `Run all` limpo no Colab · montar o ZIP · reserva |
| Qua 18 | protótipo final · reserva |
| Qui 19 | envios, de preferência pela manhã |

## 7. O que só o grupo pode fazer
1. **Commit e push** (o notebook baixa a base do GitHub).
2. **Criar a chave de um provedor** e cadastrar nos Secrets do Colab com "Notebook access". Sugestão: Groq (`GROQ_API_KEY`), que é o primeiro da lista do notebook.
3. **Rodar o notebook no Colab** e enviar qualquer erro.
4. **Escrever as 8 respostas de referência**, lendo os documentos indicados em cada pergunta (15 a 20 minutos).
5. **Ler e revisar os 5 documentos** da base e registrar o uso de IA no `6_Chat_Log.txt`.
6. **Prints, vídeos, `5_certificacao.txt` e `7_demo_video_url.txt`.**
7. **Copiar o GTFS oficial** para `data\raw\sptrans_gtfs.zip` (o arquivo de lá ainda é a cópia de 10/11).
8. **Confirmar com o professor de MMC** o canal de envio.

## 8. Riscos abertos
| Risco | Efeito | O que fazer |
|---|---|---|
| Notebook nunca rodou com modelo real | ajustes de versão, de prompt ou de limite de uso só aparecem no Colab | rodar até sexta |
| Modelo pequeno não segue o formato do agente | o agente gasta voltas e pode não chegar à resposta | trocar a ordem da lista para um modelo maior (Cerebras ou Hugging Face, `gpt-oss-120b`) |
| Limite de uso do plano gratuito no RAGAS (64 avaliações) | métricas vazias | rodar de novo mais tarde ou com outro provedor; o texto de análise avisa quando o juiz falha |
| Relatório PDF da MLAM não existe | −2 pontos | é o próximo passo |
| Acurácia do item 06 da MLAM abaixo do chute da maioria no limiar escolhido | pergunta na correção | já explicado no notebook; a tabela mostra também o limiar 0,5 |
