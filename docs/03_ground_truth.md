# Ground truth — o que é e como definir

**Ground truth = a resposta correta de cada pergunta de teste, escrita por nós lendo os documentos** — não pelo modelo.
O RAGAS compara a resposta do sistema (e os trechos recuperados) com ela:
- `context_recall`: os trechos recuperados contêm o que a ground truth exige?
- `context_precision`: os trechos certos vieram no topo?
- `faithfulness` / `answer_relevancy`: a resposta é sustentada pelo contexto e responde a pergunta?

⚠️ Regra: se a ground truth for gerada por IA → critério 7 cai para ≤ 1,0. Escreva à mão, depois dos documentos prontos, e **antes** de rodar o sistema.

## Como escrever uma boa ground truth
- Curta, factual, completa (1–3 frases), com o detalhe decisivo e o doc de onde vem.
- Para armadilha: dizer qual documento prevalece e por quê (data).

## Conjunto (preencher após escrever os docs)
| # | Nível | Pergunta | Ground truth (escrita à mão) | Docs necessários |
|---|---|---|---|---|
| 1 | 1 simples | Qual o horário do primeiro ônibus da linha ___ em dia útil? | | doc_02 |
| 2 | 1 simples | Quais pontos da linha ___ são acessíveis? | | doc_01 |
| 3 | 1 simples | Quem tem direito à gratuidade? | | doc_04 |
| 4 | 1 simples | Onde fica o terminal ___? | | doc_01 |
| 5 | 2 armadilha | A linha ___ passa no domingo? | (portaria posterior suprimiu) | doc_02 + doc_03 |
| 6 | 2 armadilha | Meu pai de 68 anos anda de graça no sábado? | (faixa condicional) | doc_04 |
| 7 | 2 armadilha | O terminal ___ está funcionando? | (comunicado mais recente contradiz) | doc_01 + doc_05 |
| 8 | 2 armadilha | Estudante paga no feriado? | (só dias letivos) | doc_04 |
