# Auditoria geral e plano até a entrega (posição em 11/11/2026, atualizada à tarde)

Prazo final: **19/11 às 23h59**. Protótipo: 18/11. Faltam 8 dias.

## 1. Resumo
| Frente | Situação | Estimativa |
|---|---|---|
| Motor de dados do produto | pronto, validado e documentado | 90% |
| MMC | notebooks das duas etapas prontos, com os integrantes | 95% |
| MLAM | base, notebooks dos itens 02 a 06 e README prontos; falta relatório PDF e publicação | 75% |
| Prompt & AI | base documental (5 documentos) e 3 ferramentas testadas; falta o notebook inteiro | 20% |
| App (Gradio) e deploy | não iniciado | 0% |
| Pitch (vídeo) | roteiro existe; nenhum material produzido | 10% |
| Simulação 3D | não iniciada (opcional, corte em 17/11) | 0% |

**O risco do projeto mudou de lugar.** As duas disciplinas de cálculo estão adiantadas. Prompt & AI vale 10 pontos, tem a rubrica mais longa (8 critérios, 7 arquivos) e está no zero. Pelo cronograma original, os 5 documentos do RAG deveriam ser escritos hoje. Do dia 12 em diante, o trabalho deve ser quase todo em Prompt & AI.

**Commit e push feitos em 11/11** (`52a079e`). O que foi produzido depois disso (base documental, ferramentas, nomes dos integrantes) ainda precisa de novo commit.

**Integrantes das entregas:** Davi Queiroz Zuolo (RM 571669), Gustavo Zagato Bottechia (RM 569420) e Daniel Vilela Mana (RM 571632). Com três nomes, Prompt & AI segue o escopo de trio: 8 perguntas no RAGAS (4 + 4), 4 guardrails e documento extra (a base tem 5).

## 2. O que foi feito
### Produto (motor de dados)
- Download reproduzível: OD 2017, GTFS, zonas OD, distritos e subprefeituras (`scripts/baixar_od2017.py`, `scripts/baixar_dados.py`).
- Geografia zona → distrito → subprefeitura → região (`core/analytics/geo.py`).
- Oferta: frota reconstruída do GTFS por área e hora (`core/analytics/oferta.py`).
- Demanda: embarques e carga a bordo por trecho de ônibus (`core/analytics/demanda.py`).
- Redistribuição: alvo inteiro com piso de cobertura, matriz T, verificação e indicadores (`core/frota/`).
- Modelo preditivo: funil de limpeza, treino agrupado por família, limiar por validação cruzada (`core/analytics/preparo.py`, `modelo.py`).
- Pipeline que grava as tabelas agregadas (`scripts/passo0_pipeline.py` → `data/processed/`).
- 54 testes automáticos; notebook explicativo com 13 checagens (`notebooks/01_motor_de_dados_explicado.ipynb`).
- Documentação: `docs/08_modelo_produto.md` (D10) e este documento.

### Entregas extraídas em 11/11
- **MMC:** `entregas/mmc/01_etapa1_reconstrucao.ipynb` e `02_etapa2_redistribuicao.ipynb`, executados, mais README.
- **MLAM:** `entregas/mlam/01_preparacao.ipynb`, `02_normal_hipoteses.ipynb`, `03_regressoes.ipynb`, executados; `dados/od2017_sp_trabalho.csv`; README com os tópicos do item 08d.

## 3. Decisões registradas em 11/11 (D11)
| Decisão | Motivo |
|---|---|
| Notebooks de entrega são **autossuficientes** (não importam `core/`) | o avaliador roda a pasta da disciplina sem montar o projeto inteiro; a lógica é a mesma do produto, copiada em poucas linhas |
| MLAM 03: população de referência = todos os trabalhadores; amostra a) 20 que vão de carro (cauda esquerda), b) 25 que vão de ônibus (cauda direita) | sortear a amostra da própria população testaria uma hipótese sem conteúdo; assim cada teste responde a uma pergunta do problema |
| MLAM 02: variável = duração das viagens de ônibus | é a variável com interpretação direta para o problema, e a assimetria rende a discussão do item b |
| MLAM 06 na entrega: modelo de 4 quantitativas como principal, ampliado como complemento | o enunciado pede pelo menos 3 quantitativas; o ampliado mostra o que melhora o ajuste |
| MMC: frota-alvo = necessidade, sem piso de cobertura | no enunciado a necessidade total é igual à frota (72); o piso é uma decisão do produto real, onde a regra pura esvaziava a periferia |
| API Olho Vivo fica fora do MVP | não atende critério de nenhuma disciplina; entra como evolução no pitch. O token nunca vai para o repositório |

## 4. O que tem × o que falta, por disciplina
### MMC (Etapa 1: 5 pts · Etapa 2: 5 pts)
| Item | Situação |
|---|---|
| 1a variáveis · 1b modelo · 1c forma matricial | pronto |
| 1d unicidade (determinante = 3, posto 4, Rouché–Capelli, Laplace à mão) | pronto |
| 1e solução em Python · 1f verificação | pronto: (12, 20, 16, 24) |
| 2a necessidade · 2b desequilíbrios | pronto: (14, 19, 18, 21); déficit no Norte e no Leste |
| 2c política e critérios · 2d transformação linear · 2e matriz e coeficientes | pronto |
| 2f demonstrações (conservação, não negatividade, inteiro) | pronto, com checagem numérica |
| Avaliação antes × depois | pronto: 160 passageiros sem vaga → 0, com 4 ônibus movidos |
| Integrantes nos notebooks e no README | pronto |

**Como entrega:** os dois notebooks de `entregas/mmc/`. O projeto tem só as Etapas 1 e 2 (confirmado pelo Davi em 11/11). A dúvida sobre uma "Etapa 3" vinha de uma nota em `docs/02_materias.md`, escrita porque a contextualização do enunciado fala em reconstruir, redistribuir **e avaliar os resultados**, mas só lista duas etapas; a avaliação antes × depois está no fim do notebook da Etapa 2. Falta confirmar o canal de envio (Portal) e se o professor quer PDF além do notebook.

**Atenção:** o enunciado da MMC diz que a política deve ser desenvolvida pela própria equipe. A regra é a que definimos juntos; é preciso saber explicá-la e defender cada coeficiente da matriz sem consultar o notebook.

### MLAM (10 pts; −1 por item ausente; −2 por entrega errada no portal)
| Item | Pts | Situação |
|---|---|---|
| 01 Base real e justificada | — | pronto: OD 2017, com fonte e endereço |
| 02 Normal: P(X < média), P(X > mediana), classificação | 1,0 | pronto |
| 03 Testes Z (n = 20, α = 6%, esquerda; n = 25, α = 9%, direita) | 1,0 | pronto |
| 04 Bivariada (a–f) | 2,0 | pronto |
| 05 Múltipla (a–f) | 2,0 | pronto, com 4 quantitativas |
| 06 Logística (a–c) | 2,0 | pronto |
| 07 **Relatório estatístico em PDF** | 2,0 | **falta** |
| 08a csv + fonte + limpeza reproduzível | — | pronto |
| 08b notebooks com saídas | — | pronto |
| 08c PDF | — | **falta** (é o item 07) |
| 08d README | — | pronto |
| Repositório com tudo commitado | — | commit feito; **confirmar que está público** e commitar as mudanças da tarde |
| **.txt do portal** (nome, RM, link) | — | **falta** |

**Como entrega:** um único arquivo `.txt` no Portal com nome completo, RM e o link do repositório GitHub. O repositório precisa estar **público** e abrir sem pedir autorização; conta a versão que estiver lá no prazo.

**Pontos a conferir:** (1) a classificação do evento no item 02 usa a escala impossível / improvável / tão provável quanto improvável / provável / certo; trocar pelos termos usados em aula, se forem outros. (2) No item 06 a acurácia no limiar escolhido (0,63) fica abaixo da de prever sempre "não usa" (0,79). Está explicado no notebook e a tabela mostra também o limiar 0,5 (0,78), mas é a pergunta mais provável da correção.

### Prompt & AI (10 pts · ZIP com 7 arquivos · notebook roda no Colab)
| Critério | Peso | Situação |
|---|---|---|
| 1 Entrega (ZIP, Run all, vídeo ≤ 3 min, sem chave) | 1,0 | falta tudo |
| 2 Base documental (≥ 2 docs, armadilha, 2 chunkings comparados) | 1,0 | **5 documentos prontos** em `base_documental/` (3 armadilhas + injection); falta a comparação de chunking |
| 3 RAG em LCEL com citação e "não sei" | 1,5 | falta |
| 4 Agente (≥ 2 ferramentas, uma calcula, erro controlado, ≤ 6 chamadas) | 1,5 | **3 ferramentas prontas e testadas** em `core/agent/ferramentas.py` (15 testes, erros controlados); falta montar o agente |
| 5 Gradio com histórico e fontes | 0,7 | falta |
| 6 Guardrails (3; 4 no escopo de trio) | 1,0 | falta |
| 7 RAGAS (perguntas com ground truth própria, métricas reais, explicação) | 2,0 | falta; **a ground truth é escrita pelo Davi, à mão** |
| 8 README (diagrama, prints, decisões, armadilha) | 1,3 | falta |
| Bônus (até +1,0) | — | pergunta composta com 2 ferramentas |

**Como entrega:** `GS2026_2_<TURMA>_<NOME_GRUPO>.zip` no Portal, com `1_Notebook_GS2026_2.ipynb` (seções 0 a 8 com os títulos exatos), `2_base_documental/`, `3_avaliacao_ragas.json`, `4_README.md`, `5_certificacao.txt`, `6_Chat_Log.txt`, `7_demo_video_url.txt`.

**O que depende só do Davi:** escrever a ground truth; revisar e assumir os documentos; registrar o uso de IA no `6_Chat_Log.txt`; gravar o vídeo; cadastrar `OLLAMA_API_KEY` nos Secrets do Colab.

**Condição técnica:** o notebook roda no Colab, então tudo o que ele lê (documentos, tabela de fluxos) precisa estar em endereço público ou ser criado pelo próprio notebook.

## 5. O que falta para o projeto geral e para o pitch
| Item | Para quê | Situação |
|---|---|---|
| App Gradio com 3 abas (Cidadão, Gestor, Dados) | protótipo de 18/11; a aba Cidadão é o critério 5 de Prompt & AI | falta |
| Aba Gestor: mapa de pressão por zona e tabela antes × depois | pitch (trecho do gestor) | dados prontos; falta a tela |
| Deploy no Hugging Face Spaces | protótipo acessível por link | falta |
| GTFS oficial da SPTrans | trocar a cópia de terceiros | o arquivo em `data/raw/sptrans_gtfs.zip` ainda é a cópia baixada em 10/11 (mesmo conteúdo, byte a byte); o download oficial não chegou a essa pasta |
| Vídeo do pitch (≤ 3 min) | concorrer ao top 3 | falta |
| Vídeo de Prompt & AI (≤ 3 min) | critério 1 | falta |
| Simulação 3D | fecho do pitch | opcional; só se as 3 entregas estiverem prontas em 17/11 |

### Números que o pitch pode usar (todos medidos)
- 9,7 milhões de embarques de ônibus por dia na OD 2017; 43% deles ficam invisíveis se só o "modo principal" for contado.
- Às 17h, a ocupação média vai de 0,20 (Perus) a 0,80 (Pinheiros, Butantã): uma diferença de 4 vezes com a mesma frota.
- Redistribuindo 1.193 ônibus (9% da frota em operação), a faixa cai para 0,25–0,56, sem comprar nenhum veículo e sem tirar mais de 20% de nenhuma área.
- Viagem de ônibus ao trabalho: 58 min em média, contra 39 min na média de todos os modos.
- Cada carro a mais em casa corta pela metade a chance de usar ônibus.

### O que o pitch **não** pode afirmar
- Que a superlotação acaba: o modelo mede a ocupação média da linha, não o trecho mais cheio.
- Economia em reais: continua sendo hipótese (exige dado operacional).
- Que a espera cai em toda hora: às 6h ela sobe 0,25 min.

### Regiões no pitch
A política é calculada em 32 subprefeituras. No pitch aparece o mesmo cálculo somado nas 5 regiões oficiais da Prefeitura (Centro, Norte, Sul, Leste, Oeste), porque uma tabela de 5 linhas cabe num slide e repete a estrutura do enunciado da MMC. É apresentação, não outro modelo. Às 17h: Oeste 0,73 e Centro 0,63 contra Norte 0,42 e Leste 0,46.

## 6. Entradas do modelo e peso de cada uma
Modelo completo no teste: AUC 0,814 · acurácia 0,738 · F1 0,547. A tabela mostra o quanto cada medida cai quando a entrada é retirada.

| Entrada | Queda na AUC | Queda na acurácia | Queda no F1 | AUC usando só ela |
|---|---|---|---|---|
| Distância casa–trabalho (linear + log) | 0,080 | 0,068 | 0,075 | 0,643 |
| Carros no domicílio | 0,020 | −0,018 | 0,017 | 0,665 |
| Renda per capita (log) | 0,007 | 0,000 | 0,008 | 0,667 |
| Ocupação | 0,007 | −0,012 | 0,009 | 0,667 |
| Vínculo CLT | 0,004 | 0,010 | 0,007 | 0,609 |
| Idade | 0,000 | −0,001 | −0,001 | 0,557 |
| Horário de pico | 0,000 | 0,011 | 0,005 | 0,501 |

- A **distância** é a entrada que mais pesa: sem ela a AUC cai de 0,81 para 0,73. O ganho vem da forma não linear (sobe até ~6 km e depois cai).
- **Carros, renda e ocupação** medem coisas parecidas (condição socioeconômica): cada uma sozinha chega a AUC 0,67, mas tirar uma só custa pouco, porque as outras compensam.
- **Idade e horário de pico** não contribuem. Podem sair do modelo.
- Quedas negativas na acurácia aparecem porque o limiar é reescolhido a cada modelo; a AUC é a medida estável para comparar.
- Fora das entradas, o que mais mexe na acurácia é o **limiar**: 0,806 no limiar 0,5 contra 0,738 no limiar 0,24, com o recall indo de 0,29 para 0,75.

## 7. Cronograma revisto
| Dia | Trabalho | Quem |
|---|---|---|
| Qua 11 | ✅ commit e push · ✅ 5 documentos do RAG · ✅ ferramentas do agente · GTFS oficial (pendente) | Davi revisa os documentos |
| Qui 12 | ground truth à mão · chunking A × B · Chroma · RAG em LCEL com citação | Davi escreve a ground truth |
| Sex 13 | agente e 3 ferramentas · guardrails | — |
| Sáb 14 | RAGAS v1 × v2 · interface Gradio (aba Cidadão) | — |
| Dom 15 | abas Gestor e Dados · relatório PDF da MLAM | — |
| Seg 16 | relatório da MMC · README de Prompt & AI · deploy | — |
| Ter 17 | Run all limpo no Colab · decisão sobre a simulação | Davi testa no Colab |
| Qua 18 | protótipo final · vídeos | Davi grava |
| Qui 19 | ZIP · .txt · envio | Davi envia |

## 8. Pendências que dependem do Davi
1. Novo commit e push; confirmar que o repositório está público.
2. Copiar o GTFS oficial baixado para `data/raw/sptrans_gtfs.zip` (substituindo o atual).
3. Ler e revisar os 5 documentos de `base_documental/` e registrar o uso de IA no `6_Chat_Log.txt`.
4. Informar a turma (para o nome do ZIP de Prompt & AI).
5. Confirmar os termos de classificação de evento usados na aula de MLAM.
6. Escrever a ground truth do RAGAS depois que os documentos estiverem prontos.
7. Guardar o token da Olho Vivo e a `OLLAMA_API_KEY` fora do repositório.

## 9. Base documental e ferramentas (feito em 11/11 à tarde)
- **Documentos simulados** (`base_documental/`): itinerários (doc_01), tabela de horários (doc_02), portaria que altera a operação (doc_03), gratuidades (doc_04) e comunicado de obras (doc_05). Três linhas fictícias (714A-10, 502C-10, 318N-10) e o Terminal Ipê Roxo. Todos trazem aviso de documento simulado.
- **Armadilhas:** desatualização (doc_02 × doc_03: domingo da 714A-10 e primeira partida da 318N-10), faixa condicional (doc_04: idade e dia), contradição (doc_01 × doc_05: plataforma C) e uma instrução maliciosa dentro do doc_05.
- **Ferramentas** (`core/agent/ferramentas.py`): `calcular_proximo_horario(linha, hora, dia)` calcula a partir das faixas de intervalo; `verificar_gratuidade(idade, pcd, estudante, dia)` aplica o doc_04; `consultar_fluxo(origem, destino, hora)` consulta os fluxos reais da OD. Erros voltam como mensagem, sem exceção.
- **Coerência entre RAG e ferramenta:** as ferramentas leem `operacao_vigente.json`, que já reflete a portaria. Se lessem a tabela antiga, o agente e o RAG se contradiriam.
- **Não testado ainda:** nada que dependa do modelo (RAG, agente, RAGAS). O ambiente onde o código roda não alcança o Ollama Cloud; o notebook precisa ser executado no Colab pelo Davi.
