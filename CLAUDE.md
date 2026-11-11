# CLAUDE.md — Linha Certa (GS 2026.2 FIAP · Citizen Tech)

## Contexto
Projeto individual que entrega 3 disciplinas num só produto: Prompt & AI, Modelagem Matemática e Computacional (MMC), Modelagem Linear para ML (MLAM). Meta do produto: ônibus de São Paulo circulando de forma inteligente + comunicação Estado ↔ cidadão. Prazo final: 19/11/2026 23h59.
Leia antes de agir: `docs/00_contrato_pitch.md`, `docs/01_decisoes.md`, `docs/02_materias.md`, `docs/05_variaveis_modelo.md`, `docs/08_modelo_produto.md` (D10: modelo implementado; prevalece sobre a D9), `docs/09_auditoria_e_plano.md` (situação, pendências e cronograma revisto).

## Regras inegociáveis
- `OLLAMA_API_KEY` nunca aparece em código, notebook, print, commit ou ZIP. No Colab: `userdata.get('OLLAMA_API_KEY')`.
- Prompt & AI: notebook roda com Run all no Colab; seções com os títulos exatos de 0 a 8; pipeline em LCEL; sem API paga.
- **Ground truth das 8 perguntas é escrita pelo aluno. Nunca gerar nem sugerir texto de ground truth.** Também nunca inventar resultado do RAGAS.
- MLAM: só dados reais (OD 2017). Toda limpeza reproduzível em código. Notebooks entregues com as saídas.
- MMC: entrega separada com os dados do enunciado; não misturar com a OD.
- Todo uso de IA no Prompt & AI deve ser registrado em `entregas/prompt_ai/6_Chat_Log.txt`.

## Dados
- OD 2017: `data/raw/od_sao_paulo_2017_not_harmonized.csv.gz` (`sep=';'`), dicionário em `data/dicionario/`. Recorte SP: `muni_o == 36 & muni_d == 36`. Ônibus SP: `modoprin == 4`. Peso: `fe_via`.
- Modelamos fluxos agregados (zona × hora), nunca indivíduos.
- Demanda de ônibus = trechos com `modo1..4 == 4` (não `modoprin == 4`, que perde 43% dos embarques). Na MLAM o alvo continua `modoprin == 4`.
- Oferta: GTFS em `data/raw/sptrans_gtfs.zip` (`scripts/baixar_dados.py`). Pipeline: `python scripts/passo0_pipeline.py` grava `data/processed/`.
- Nada sai publicado com menos de 10 viagens amostradas por célula (`MIN_AMOSTRA`).
- Testes: `python -m pytest tests`.

## Convenções
- Python 3.11+, versões travadas em `requirements.txt`.
- Código compartilhado em `core/`; cada pasta em `entregas/` contém só o que a disciplina pede.
- Comentários e documentação em português.
