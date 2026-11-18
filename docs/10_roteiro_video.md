# Roteiro do vídeo de Prompt & AI (3 min)

Formato: gravação de tela do Colab, sem áudio, com narração gravada por cima depois.
Regra do enunciado: até 3 minutos e os três integrantes se apresentam no início.

## Antes de gravar a tela
1. Rodar o notebook inteiro e deixar todas as saídas visíveis.
2. Recolher as barras de progresso da seção 7 (clicar no "..." à esquerda da saída) para não rolar 16 barras.
3. Zoom do navegador em 80% (`Ctrl -`): cabe a saída inteira de cada seção na tela.
4. Esconder o painel de Secrets. Nenhuma chave pode aparecer.
5. Gravar em 1080p, rolagem lenta e contínua. Gravar uns 10 s a mais em cada parada e cortar depois.

## Tempo por seção

| Tempo | Duração | O que fica na tela | Narração |
|---|---|---|---|
| 0:00–0:20 | 20 s | rosto dos três, ou slide com nomes e RMs | **Davi:** "Somos o grupo Linha Certa, da turma 1CCPK. Eu sou Davi Queiroz Zuolo, RM 571669." **Gustavo:** "Gustavo Zagato Bottechia, RM 569420." **Daniel:** "Daniel Vilela Mana, RM 571632." **Davi:** "O Linha Certa é um assistente de mobilidade urbana que só responde com fonte: cada informação vem com o documento de onde saiu." |
| 0:20–0:37 | 17 s | seção 1: tabela dos 5 documentos | "A base tem cinco documentos municipais simulados, escritos pelo grupo, com metadados de doc_id e data. Três são armadilhas de propósito: a portaria de setembro contradiz a tabela de horários de março, a gratuidade muda aos 65 anos, e o comunicado de obras contradiz o guia do terminal." |
| 0:37–0:53 | 16 s | seção 1: tabela A × B e a justificativa | "Comparei duas estratégias de chunking. O critério não foi o tamanho do trecho, e sim recuperar o documento antigo e o que o corrige: responder só com o antigo é responder errado. A de mil caracteres acertou três das três armadilhas; a de quinhentos, duas." |
| 0:53–1:05 | 12 s | seção 2: chunks indexados e a busca com `distance` | "Os embeddings são multilíngues e rodam no próprio Colab, sem chave. Cada trecho vai para o ChromaDB com o doc_id e a data, que é o que permite citar a fonte depois." |
| 1:05–1:25 | 20 s | seção 3: as três respostas | "O pipeline é LCEL: retriever, prompt, modelo, parser. O contexto entra ordenado do documento mais recente para o mais antigo, com a data no rótulo, para o modelo ter critério quando dois documentos se contradizem. Ele cita o doc_id de cada informação e, fora da base, diz que não sabe em vez de inventar." |
| 1:25–1:47 | 22 s | seção 4: tabela das ferramentas e o trace (rolar pelos três blocos) | "O agente ReAct tem quatro ferramentas e no máximo seis chamadas. O modelo decide quando chamar, mas o código decide o que a ferramenta devolve: horário e gratuidade nunca saem do modelo. No trace, a linha inexistente devolve erro controlado e o agente repassa o problema sem inventar. Na última pergunta ele encadeia duas ferramentas sozinho." |
| 1:47–1:59 | 12 s | seção 5: interface Gradio, com uma pergunta já respondida | "A interface tem histórico, para entender perguntas como 'e no sábado?', e mostra as fontes ao fim de cada resposta. A chave fica nos Secrets do Colab e nunca aparece." |
| 1:59–2:21 | 22 s | seção 6: os 4 testes, depois a célula da injection na fonte | "São quatro guardrails. Escopo: recusa o que não é transporte. Prompt injection em dois lugares, na pergunta e na fonte: o doc_05 tem uma instrução maliciosa plantada, removida na carga, que não chega ao índice. LGPD: recusa dado de pessoa. E limite de confiança: resposta sem citação vira 'não há informação'. Três deles têm teste automatizado." |
| 2:21–2:53 | 32 s | seção 7: linha do juiz, tabela v1, tabela v2, médias, e a leitura dos números | "A avaliação tem oito perguntas, quatro simples e quatro armadilhas, com resposta de referência conferida contra os documentos. O juiz é o Gemini, de outro provedor, para o agente não corrigir a própria prova. Comparei as duas versões de chunking com o mesmo juiz e as mesmas perguntas: a de mil caracteres ganha na recuperação, que é onde as armadilhas se decidem. A pior pergunta é o horário da 502C-10: vem o documento certo, mas não a linha da tabela. Por isso proponho busca híbrida com BM25 e reranking: código é termo exato, e embedding aproxima sentido." |
| 2:53–3:00 | 7 s | seção 8: conclusão | "Para produção faltam documentos oficiais com atualização automática, avaliação contínua e horário em tempo real pela API Olho Vivo." |

## Observações
- A narração não cita nenhuma média do RAGAS de propósito: as métricas mudam de uma execução para outra, e uma fala com número errado contra a tabela na tela é o tipo de erro que a banca vê primeiro. Quem dá os números é a tela.
- Se quiser citar um número, leia-o da tela gravada, não de memória nem de uma versão anterior do README.
- Gravar o áudio só depois da execução final, com o vídeo já montado na frente.
