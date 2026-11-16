# Entrega MMC — Mobilidade Urbana Inteligente

## Integrantes
| Nome completo | RM |
|---|---|
| Davi Queiroz Zuolo | 571669 |
| Gustavo Zagato Bottechia | 569420 |
| Daniel Vilela Mana | 571632 |


Resolução das duas etapas do projeto com os dados do enunciado (4 regiões, 72 ônibus).

| Arquivo | Conteúdo | Itens do enunciado |
|---|---|---|
| `01_etapa1_reconstrucao.ipynb` | variáveis, modelo, forma matricial, unicidade (determinante e Rouché–Capelli), solução em NumPy, verificação | Etapa 1, a–f |
| `02_etapa2_redistribuicao.ipynb` | necessidade, desequilíbrios, política, transformação linear, matriz T, significado dos coeficientes, demonstrações, avaliação antes × depois | Etapa 2, a–f |

## Resultado
- **Etapa 1:** Norte = 12, Sul = 20, Leste = 16, Oeste = 24. Solução única: det(A) = 3 e posto(A) = posto([A|b]) = 4.
- **Etapa 2:** necessidade = (14, 19, 18, 21). Norte e Leste em déficit de 2; Sul (+1) e Oeste (+3) em superávit. A matriz T, coluna-estocástica, leva a frota a (14, 19, 18, 21) movendo 4 ônibus, preservando os 72 e zerando os 160 passageiros sem vaga.

## Como executar
**No Google Colab:** abrir pelo link e usar `Ambiente de execução → Executar tudo`. Os notebooks não dependem de arquivos externos nem de chave.

| Notebook | Abrir no Colab |
|---|---|
| `01_etapa1_reconstrucao.ipynb` | https://colab.research.google.com/github/DaviZuolo07/CitizenTech_GS_2SEM/blob/main/entregas/mmc/01_etapa1_reconstrucao.ipynb |
| `02_etapa2_redistribuicao.ipynb` | https://colab.research.google.com/github/DaviZuolo07/CitizenTech_GS_2SEM/blob/main/entregas/mmc/02_etapa2_redistribuicao.ipynb |

**No computador:** `pip install numpy pandas matplotlib jupyter` e abrir os notebooks em ordem (`Run All`). Estão salvos com as saídas.

## Relação com o produto
A mesma regra (alvo inteiro + matriz coluna-estocástica) é a que o Linha Certa aplica aos dados reais de São Paulo em `core/frota/redistribuicao.py`. Esta entrega usa somente os dados do enunciado.
