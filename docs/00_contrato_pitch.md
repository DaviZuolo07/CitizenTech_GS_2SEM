# Contrato do projeto (Pitch)

## Em uma frase
**Linha Certa** é o assistente de mobilidade da prefeitura que responde ao cidadão *só com o que está publicado* — citando o documento — e entrega à central de operações onde falta e onde sobra ônibus.

## O problema
1. **Para o cidadão:** a informação de ônibus existe, mas está espalhada em itinerários, tabelas de horário, portarias e comunicados — e eles se contradizem. "O 714 passa no meu bairro domingo?" depende de saber qual portaria é a mais recente. Chatbots comuns *inventam* a resposta com confiança.
2. **Para a operação:** a frota é fixa e mal distribuída. Algumas regiões têm passageiro em pé esperando; outras têm ônibus ocioso.
3. **Quem sofre mais:** quem depende do transporte coletivo — em geral, menor renda, sem carro, idosos e PcD. (Hipótese a ser **provada com dados reais** na entrega de MLAM.)

## A solução — duas faces, um sistema
| Face | Quem usa | O que entrega |
|---|---|---|
| **Cidadão** | morador | Chat que responde com citação do documento, diz "não há informação na base" quando não sabe, calcula próximo horário e checa gratuidade por ferramenta (nunca "chuta"). |
| **Operador (COB)** | central da prefeitura | Painel: frota atual (reconstruída), necessidade por região, política de redistribuição com matriz e prova de que a frota total se mantém. |
| **Dados** | gestor | Evidência real de quem depende do ônibus e do que explica o tempo de viagem (Pesquisa OD 2017). |

## Por que é confiável
- Toda resposta tem **fonte rastreável** (doc_id + data de publicação).
- Erro é **medido**, não prometido: avaliação RAGAS com perguntas e respostas corretas escritas por humanos.
- **Guardrails:** recusa fora de escopo, ignora instrução maliciosa dentro de documento, protege dado pessoal (LGPD), admite quando não sabe.
- O LLM **decide quando** calcular; o **código calcula**.

## Como é implementado (visão de produto)
Documentos públicos → indexados por trecho → recuperados conforme a pergunta → modelo responde citando → guardrail confere → cidadão. Na operação: indicadores → modelo matemático → redistribuição. Tudo em ferramentas abertas e gratuitas.

## É viável?
- Usa só tecnologia existente e madura: modelo de linguagem via API (Ollama Cloud), banco vetorial (ChromaDB), interface web (Gradio), Python científico.
- Não exige hardware, sensor ou integração com sistemas da operadora para o MVP: a matéria-prima são **documentos que a prefeitura já publica**.
- Protótipo publicado gratuitamente (Hugging Face Spaces).

## É custo-benefício?
- **Custo do MVP:** ~zero (camadas gratuitas). Em produção: poucas chamadas ao modelo por pergunta (recuperação + resposta + eventualmente 1–2 tools), servidor pequeno; nenhum atendente lendo documento por documento.
- **Benefício:** desafoga telefone/guichê, reduz erro de informação ao cidadão, e a redistribuição usa a **mesma frota** (nenhum ônibus comprado) para atender melhor quem espera.
- **Argumento do pitch:** "não compramos um ônibus sequer e não inventamos uma resposta sequer."

## O que NÃO é (limites honestos)
- Não é canal oficial nem substitui a prefeitura; usa base documental simulada no protótipo.
- Não rastreia ônibus em tempo real (evolução futura via GTFS/API da operadora).
- Dados da operação de frota (MMC) são hipotéticos, fornecidos pelo desafio.

## Roteiro do vídeo-pitch (≤ 3 min)
1. (0:00–0:25) Dor: cidadão recebe informação errada; ônibus lotado num bairro, vazio no outro.
2. (0:25–0:50) Dado real: quem depende do ônibus (MLAM).
3. (0:50–1:50) Demo: pergunta armadilha respondida certa e com fonte; tentativa de injection recusada.
4. (1:50–2:30) Painel do operador: redistribuição que zera o déficit sem novo ônibus.
5. (2:30–3:00) Custo ~zero, métricas medidas, próximos passos.
