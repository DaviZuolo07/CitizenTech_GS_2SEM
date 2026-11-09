# Decisões do projeto

## D1 — Dataset base (dados REAIS → MLAM, e contexto do pitch)
**Escolha: Pesquisa Origem-Destino 2017 (Metrô-SP), microdados de viagens.**
- Real, público, oficial, aceito pela regra "sem dados fictícios" da MLAM.
- Uma linha por viagem, com variáveis do tipo (confirmar nomes no dicionário de dados):
  idade, renda familiar, nº de automóveis no domicílio, duração da viagem, coordenadas de origem/destino (→ distância), modo principal, motivo, zona.
- Variáveis derivadas planejadas:
  - `distancia_km` = distância euclidiana entre coordenadas UTM origem/destino.
  - `usa_coletivo` (0/1) = modo principal ônibus/metrô/trem.
- **Plano B:** séries de passageiros transportados SPTrans (prefeitura.sp.gov.br) — mais pobre para logística.
- Prazo para validar download + colunas: **10/11**.
- Os dados da MMC NÃO vêm daqui: são os do enunciado (hipotéticos). A OD é usada só como contexto ("a demanda real existe e é desigual").

### Como deixar o dado bom (pipeline reproduzível em `entregas/mlam/`)
1. Baixar bruto → `data/raw/` (fora do git; README cita URL e data de acesso).
2. Filtrar: viagens válidas, município de SP, modo motorizado.
3. Tratar: remover duração/renda nulas ou zeradas; outliers por IQR (documentar quantos saíram); padronizar unidades (min, km, R$).
4. Derivar `distancia_km`, `usa_coletivo`.
5. Amostrar (ex.: 5–10 mil linhas, `random_state=42`) para o .csv entregue → `data/processed/od2017_tratado.csv`.
6. Tudo em código (`01_preparacao.ipynb`) — a banca precisa conseguir reproduzir.

## D2 — Documentos do RAG (base documental)
**Origem: escritos por nós, simulando publicações da prefeitura fictícia "Município de Vale Verde"** (o briefing proíbe copiar da internet; IA pode ajudar a rascunhar, desde que revisado e registrado no Chat_Log).
Coerência: mesmas regiões Norte/Sul/Leste/Oeste da MMC.

| doc_id | Documento | Data | Papel |
|---|---|---|---|
| doc_01 | Itinerários e pontos das linhas (com ponto acessível no meio do texto) | 2026-03-02 | base; detalhe "escondido" para forçar chunking |
| doc_02 | Tabela de horários dias úteis / sábado / domingo | 2026-03-02 | base para tool de próximo horário |
| doc_03 | Portaria nº 47/2026 — suprime linha X aos domingos e altera itinerário | 2026-09-15 | **armadilha de desatualização** |
| doc_04 | Regulamento de gratuidade (≥ 65 anos, PcD; estudante só dias letivos) | 2026-01-10 | **armadilha de faixa condicional** |
| doc_05 | Comunicado de interdição de terminal + trecho com prompt injection | 2026-10-20 | **contradição** + teste de guardrail (doc extra do trio) |

Cada documento: ≥ 100 palavras, linguagem de documento público, cabeçalho de metadados:
```
titulo: ...
doc_id: doc_03
data_publicacao: 2026-09-15
tema: mobilidade
```

## D3 — Chunking (como escolher, não "porque é padrão")
Comparar **2 estratégias** com o mesmo embedding e o mesmo k:
- **A:** `RecursiveCharacterTextSplitter` 500 caracteres, overlap 50.
- **B:** 1000 caracteres, overlap 150 (ou divisão por seção/cabeçalho do documento).

Critério de decisão (tabela exigida no notebook):
| Estratégia | nº chunks | acerto do trecho certo no top-k (perguntas armadilha) | resposta final correta? |
Escolher a que recupera **os dois trechos** necessários na pergunta armadilha (ex.: horário + portaria posterior). Hipótese a testar: chunk menor separa melhor a cláusula condicional; chunk maior preserva contexto da portaria. Justificar em 3–5 linhas com o número. Repetir no RAGAS (v1 × v2) para bônus.

## D4 — Ground truth
Ver `03_ground_truth.md`.

## D5 — Stack
Python · LangChain (LCEL) · ChromaDB · Ollama Cloud · Gradio · RAGAS · NumPy/SciPy/statsmodels. Sem API paga. Sem React.
