# 🚌 Linha Certa
**Assistente de mobilidade urbana que só responde com fonte — e uma central que coloca o ônibus onde o passageiro está.**

Projeto único da Global Solution 2026.2 (FIAP · Citizen Tech) que resolve, em uma mesma solução, as entregas de:

| Disciplina | Pasta de entrega | Peça da solução |
|---|---|---|
| Prompt and Artificial Intelligence | `entregas/prompt_ai/` | Assistente do cidadão (RAG + agente + guardrails + RAGAS) |
| Modelagem Matemática e Computacional | `entregas/mmc/` | Motor de frota: reconstrução (sistema linear) e redistribuição (transformação linear) |
| Modelagem Linear para ML (MLAM) | `entregas/mlam/` | Inteligência de demanda com dados reais (Pesquisa OD 2017) |

## Estrutura
```
docs/               contrato do projeto, decisões, matriz de matérias, ground truth, cronograma
data/raw|processed  dataset real (OD 2017) — bruto fora do git, processado versionado
base_documental/    documentos simulados do município (fonte do RAG)
core/               código compartilhado (rag, agent, guardrails, frota, analytics)
app/                interface Gradio (abas Cidadão | Operador | Dados)
entregas/           cada pasta = exatamente o que a disciplina pede
notebooks/          exploração (não é entrega)
tests/              testes de guardrails e tools
```

## Como rodar o motor de dados
```
pip install -r requirements.txt
python scripts/baixar_od2017.py      # Pesquisa OD 2017 (demanda)
python scripts/baixar_dados.py       # GTFS SPTrans (oferta) e geografia
python scripts/passo0_pipeline.py    # grava as tabelas agregadas em data/processed/
python -m pytest tests
```
Modelo, resultados e limitações: `docs/08_modelo_produto.md`.

## Regra de ouro
A `OLLAMA_API_KEY` **nunca** entra no repositório, notebook, print ou ZIP. Use Secrets do Colab / variável de ambiente (`.env` está no `.gitignore`).

## Integrante
Davi Zuolo — RM: ______ · Turma: ______
