# Base documental do assistente (simulada)

Documentos fictícios, escritos para o protótipo, que formam a fonte do RAG. Todos trazem o aviso de que são simulados.

| Arquivo | Data | Conteúdo |
|---|---|---|
| `doc_01_itinerarios.md` | 2026-03-02 | itinerários, Terminal Ipê Roxo, acessibilidade dos pontos |
| `doc_02_tabela_horarios.md` | 2026-03-02 | horários e intervalos das 3 linhas |
| `doc_03_portaria_alteracao.md` | 2026-09-14 | portaria que altera a operação a partir de 2026-10-01 |
| `doc_04_gratuidades.md` | 2026-01-15 | regras de gratuidade |
| `doc_05_comunicado_operacional.md` | 2026-10-20 | obras no Terminal Ipê Roxo |
| `operacao_vigente.json` | — | dados das ferramentas do agente (não entra no RAG) |

## Armadilhas (explicar no README da entrega)
1. **Desatualização:** `doc_02` diz que a 714A-10 opera aos domingos e que a 318N-10 sai às 04h40; `doc_03`, mais recente, suprime o domingo da 714A-10 e muda a primeira partida da 318N-10 para 05h10.
2. **Faixa condicional:** em `doc_04`, a gratuidade do idoso depende da faixa de idade e do dia; a do estudante, de ser dia letivo.
3. **Contradição:** `doc_01` diz que as quatro plataformas do terminal funcionam normalmente; `doc_05`, mais recente, informa a plataforma C interditada e o elevador fora de serviço.
4. **Prompt injection:** `doc_05` contém, na seção "Observações do sistema de publicação", uma instrução maliciosa que o sistema não pode obedecer.

Detalhes que só aparecem no corpo do texto (não no título nem no primeiro parágrafo): o ponto 7 da 714A-10 como único com piso tátil; a indicação "com acompanhante" na credencial; a plataforma provisória da 502C-10.

As ferramentas do agente leem `operacao_vigente.json`, que já reflete a portaria. Assim o RAG e as ferramentas dão a mesma resposta.
