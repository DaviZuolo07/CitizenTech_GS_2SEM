# Entrega MLAM — Quem depende do ônibus para trabalhar em São Paulo?

## Integrantes
| Nome completo | RM |
|---|---|
| Davi Zuolo ______ | ______ |

## Problema e objetivo
Tema CitizenTech: mobilidade urbana. Em São Paulo a oferta de ônibus nem sempre está onde a demanda está. O objetivo das análises é descrever, com dados reais, **quem depende do ônibus para ir ao trabalho** e **quanto tempo essa viagem custa**, para apoiar decisões de distribuição da frota.

## Base de dados
- **Pesquisa Origem e Destino 2017**, Companhia do Metropolitano de São Paulo (Metrô-SP): pesquisa domiciliar real, 183.092 registros, 128 variáveis.
- Fonte original: Metrô-SP (`transparencia.metrosp.com.br`, Pesquisa Origem e Destino 2017).
- Endereço de acesso usado (espelho público do pacote R `odbr`): https://github.com/hsvab/odbr/releases/download/v0.1.0/od_sao_paulo_2017_not_harmonized.csv.gz (acesso em 09/11/2026).
- Base de análise: `dados/od2017_sp_trabalho.csv` (19.462 trabalhadores, 14 variáveis), gerada por `01_preparacao.ipynb` a partir do arquivo original. Todas as etapas de limpeza estão no notebook e são reproduzíveis.

## Arquivos
| Arquivo | Conteúdo | Itens |
|---|---|---|
| `dados/od2017_sp_trabalho.csv` | base tratada | 01, 08a |
| `01_preparacao.ipynb` | download, funil de limpeza, variáveis derivadas | 08a |
| `02_normal_hipoteses.ipynb` | distribuição normal e testes Z | 02, 03 |
| `03_regressoes.ipynb` | análise bivariada, regressão múltipla, regressão logística | 04, 05, 06 |
| `relatorio/relatorio_estatistico.pdf` | relatório estatístico | 07 |

## Como executar
```
pip install pandas numpy scipy statsmodels scikit-learn matplotlib jupyter
```
Abrir os notebooks na ordem 01 → 02 → 03, a partir desta pasta, e usar `Run All`. O `01` baixa o arquivo original da fonte se ele não estiver em `data/raw/`. Os notebooks estão salvos com as saídas.

## Dependências
Python 3.10+, pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib (versões em `requirements.txt`, na raiz).

## Síntese dos resultados
- 22% dos trabalhadores usam ônibus como modo principal; 33% usam carro.
- **Normal (02):** duração da viagem de ônibus com média 57,8 min e mediana 50 min. P(X < média) = 0,50; P(X > mediana) = 0,598 sob a normal, contra 0,489 nos dados: a duração é assimétrica à direita.
- **Testes Z (03):** quem vai de carro leva menos que a média geral de 39,5 min (z = −1,69; rejeita H0 a 6%); quem vai de ônibus leva mais (z = 4,73; rejeita H0 a 9%).
- **Bivariada (04):** duração = 23,6 + 4,7 × km; r = 0,77; R² = 0,59.
- **Múltipla (05):** renda, carros e idade acrescentam 0,003 ao R². A duração depende de onde a pessoa mora e trabalha, não de quem ela é.
- **Logística (06):** cada carro a mais reduz a chance de usar ônibus quase pela metade (razão de chances 0,53). AUC = 0,71 com 4 variáveis e 0,81 no modelo ampliado.

## Limitações
Dados de 2017 (pré-pandemia); renda atribuída pela pesquisa em 63% dos trabalhadores; distância em linha reta; duração declarada em múltiplos de 5 minutos; hipótese de normalidade não se sustenta plenamente (assimetria 0,98); os modelos mostram associação, não causa.
