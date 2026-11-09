# Contrato do projeto (Pitch) — Linha Certa · São Paulo

## Meta do produto
**Fazer os ônibus de São Paulo circularem de forma inteligente:** colocar a oferta onde e quando a demanda real está, gerar economia para o Estado com a mesma frota e abrir um canal de comunicação confiável entre o órgão de transporte e o cidadão.

## Em uma frase
Linha Certa descobre, com dados públicos, **quem precisa de ônibus, de onde para onde e a que horas**, mostra ao gestor onde a frota está mal distribuída e responde ao cidadão **só com informação oficial e citada**.

## O problema
1. **Oferta desalinhada com a demanda.** Há pontos com 40 pessoas esperando por um ônibus de 30 em 30 min e pontos com 20 pessoas e ônibus de 10 em 10. A frota existe; está no lugar errado na hora errada.
2. **Quem paga a conta é o trabalhador.** Na OD 2017, mais da metade das viagens a trabalho dentro de SP é de assalariados com carteira, e o ônibus para o trabalho concentra-se entre 6h e 8h.
3. **Comunicação quebrada.** Mudança de linha sai em portaria, comunicado e tabela diferentes, e o cidadão não acha. Chatbot genérico inventa a resposta.

## A solução — três camadas
| Camada | Para quem | O que faz | Base |
|---|---|---|---|
| **Entender a demanda** | gestor | Modelo que estima P(usa ônibus) por perfil (vínculo CLT, ocupação, renda, carros, distância, horário) e agrega em fluxos zona→zona por hora | Pesquisa OD 2017 (dado real) |
| **Redistribuir a oferta** | operação | Compara demanda × oferta por corredor/hora e propõe redistribuição da frota preservando o total (álgebra linear) | modelo matemático |
| **Falar com o cidadão** | morador | Assistente que responde com citação do documento oficial, admite quando não sabe, calcula horário e consulta fluxos por ferramenta | RAG + agente |

## Princípios (o que nos diferencia)
- **Modelamos fluxos, não pessoas.** Nenhum dado individual: tudo agregado por zona e hora, alinhado à LGPD.
- **Resposta com fonte, erro medido.** Toda resposta cita o documento; a precisão é medida (RAGAS), não prometida.
- **O modelo decide, o código calcula.** O LLM nunca inventa um horário.

## Viabilidade
- 100% dados públicos (OD 2017; GTFS da SPTrans; Censo/IBGE como camada opcional).
- 100% ferramentas abertas ou gratuitas: Python, ChromaDB, Gradio, LLM via Ollama Cloud, Hugging Face Spaces.
- Nenhum hardware, sensor ou integração obrigatória com a operadora no MVP.

## Custo-benefício
- **MVP:** custo próximo de zero (camadas gratuitas).
- **Benefício:** mesma frota, menos quilômetro rodado vazio, menos espera onde a demanda é maior, menos atendimento por telefone e guichê.
- **Honestidade:** a economia em R$ é uma *hipótese medível* (exige dado operacional da SPTrans); não inventamos números.
- **Frase do pitch:** "Não compramos um ônibus sequer. Não inventamos uma resposta sequer."

## Limites declarados
- OD 2017 é pré-pandemia (home office mudou parte da demanda); serve como linha de base, com atualização prevista pela próxima OD.
- Não é canal oficial; os documentos do assistente são simulados no protótipo.
- Sem rastreamento em tempo real no MVP (evolução: API Olho Vivo / GTFS-RT).

## Roteiro do pitch (≤ 3 min)
1. 0:00–0:20 — Dor: 40 pessoas no ponto Y esperando 30 min; ônibus vazio no ponto X.
2. 0:20–0:50 — Dado real: quem anda de ônibus para trabalhar em SP e a que horas (MLAM).
3. 0:50–1:30 — Gestor: mapa de fluxos e redistribuição sem ônibus novo (MMC).
4. 1:30–2:20 — Cidadão: pergunta armadilha respondida com fonte; tentativa de injection recusada (Prompt & AI).
5. 2:20–2:45 — (se existir) simulação 3D antes × depois.
6. 2:45–3:00 — Custo ~zero, métricas medidas, próximos passos.
