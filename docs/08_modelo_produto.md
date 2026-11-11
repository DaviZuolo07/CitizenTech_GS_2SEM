# D10 — Modelo matemático do produto (Passo 0, implementado em 10/11)

Registro do que foi aprovado e implementado no Passo 0. Onde este documento contradiz a D9 ou o handoff, vale este.

## Decisões aprovadas (10/11)
1. **Demanda base é a observada na OD**, não P̂ × viagens. A regressão logística (MLAM 06) fica para cenários "e se" e para a entrega da disciplina.
2. **Política em subprefeitura (32) × hora.** As 5 regiões (Centro, Norte, Sul, Leste, Oeste) ficam para o pitch.
3. **Capacidade (80) e lotação-alvo (0,85) são parâmetros**, com sensibilidade em 60/80/100.
4. **Terceira ferramenta do agente: `consultar_fluxo`** (não `consultar_status_linha`).

## Quatro ajustes que os dados impuseram (decididos durante a implementação)
| Ajuste | Evidência | Efeito |
|---|---|---|
| **A unidade de demanda é o trecho de ônibus, não a viagem com `modoprin == 4`** | `modoprin == 4` soma 5,52 mi de viagens/dia; contando todo trecho com `modo1..4 == 4` são 9,72 mi de embarques/dia. Quem vai de ônibus até o metrô tem modo principal "metrô" | `modoprin` deixaria 43% dos embarques de fora. O embarque de cada trecho é localizado na zona de origem ou de transferência (`zona_t1..t3`). **A MLAM não muda**: lá o alvo continua `usa_onibus = (modoprin == 4)` |
| **A carga a bordo é repartida ao longo do trajeto** (reta embarque→desembarque, proporcional ao comprimento em cada área) | Repartir 50/50 entre embarque e desembarque fazia a Sé aparecer com ocupação 1,09 às 17h. Com o trajeto, cai para 0,63 | O 50/50 era incoerente com a frota, que é repartida pelas paradas ao longo da linha. O "gargalo no Centro" era artefato do método |
| **Fluxos para o agente em subprefeitura × faixa do dia**, não distrito × hora | Com o mínimo de 10 viagens amostradas por célula, distrito × hora publica 24 células (1,3% das viagens); subprefeitura × faixa publica 637 (68%); subprefeitura × dia, 388 (84%) | `consultar_fluxo(origem, destino, hora)` converte a hora em faixa e cai para o dia inteiro quando a célula não existe |
| **Piso de cobertura: nenhuma área cede mais de 20% da frota numa hora** (`PERDA_MAXIMA`) | A regra proporcional pura tirava 55% da frota de Parelheiros às 17h (162 → 73 ônibus; intervalo médio de 25 para ~55 min) | A regra pura iguala a lotação à custa da periferia extrema, o oposto do que o pitch defende. O valor 20% é uma escolha de política, não um dado |

## Modelo implementado
**Geografia.** Zona OD → distrito → subprefeitura → região, por ponto interno da zona dentro do distrito do GeoSampa. 342 zonas, 96 distritos, 32 subprefeituras; os nomes de distrito do arquivo da OD conferem em 100% das zonas.

**Oferta (GTFS → frota).** Para cada viagem-modelo (linha e sentido) e hora:
- partidas por hora `f = 3600 / headway_secs`;
- **frota em operação `n = duração da viagem × f`** (Lei de Little). O GTFS não informa a frota; ela é reconstruída, como na Etapa 1 da MMC;
- repartição por área: `x = S·n`, onde `s(viagem, área)` é a fração das paradas da viagem naquela área. Cada coluna de S soma 1, então **x preserva a frota total** (conferido: soma regional = soma bruta em todas as horas).

**Demanda (OD → embarques e carga).**
- embarques `λ(área, hora) = Σ fe_via` dos trechos de ônibus embarcados na área, pela hora de saída da viagem;
- tempo a bordo do trecho = (duração − caminhada na origem − caminhada no destino) × fração da distância em linha reta daquele trecho. Inclui a espera, então é teto. Média: 28,8 min;
- **carga `L(área, hora) = Σ fe_via × horas a bordo`** (passageiros a bordo em média), repartida pelo trajeto;
- necessidade `n* = L / (lotação-alvo × capacidade)`.

**Política (o que vai para a MMC).**
- alvo inteiro `x̃`: proporcional a `n*`, mesma soma de `x`, respeitando o piso `⌈(1 − perda máxima)·x⌉`; arredondamento pelo maior resto (Hamilton);
- matriz `T`: na coluna de quem cede, a diagonal é `x̃/x` e o restante vai a quem tem falta, na proporção da falta; quem não cede tem coluna canônica;
- propriedades verificadas em código a cada execução: colunas somam 1, `T ≥ 0`, `Σ Tx = Σ x`, `Tx = x̃` inteiro;
- `T` é montada a partir do diagnóstico (depende de `x`); uma vez fixada, `x ↦ Tx` é linear.

**Indicadores.** Ocupação `L / (C·x)`; espera = intervalo médio das linhas da área ÷ 2; não embarcados `λ·max(0, 1 − C·x/L)`; lugares ociosos `max(0, C·x − L)`. Depois da redistribuição o intervalo da área escala por `x/x̃`.

## Resultados desta execução (C = 80, piso de 20%)
| | 6h (pico de embarques) | 17h (pico de carga) |
|---|---|---|
| Embarques na hora | 1.077.495 | 948.100 |
| Frota em operação (reconstruída) | 15.606 | 13.320 |
| Ônibus realocados entre subprefeituras | 1.314 | 1.193 |
| Ocupação média por subprefeitura (mín–máx), antes | 0,24 – 0,71 | 0,20 – 0,80 |
| Idem, depois | 0,30 – 0,46 | 0,25 – 0,56 |
| Espera média ponderada pelos embarques, antes → depois | 7,52 → 7,77 min | 8,69 → 8,37 min |

- 17h: os maiores ganhos são Pinheiros (+231), Butantã (+215) e Mooca (+168). Pinheiros, Butantã e Vila Mariana estavam a ~0,80; cedem as áreas a ~0,20–0,24 (Perus-Anhanguera, Cidade Tiradentes, Parelheiros), limitadas ao piso.
- 6h: os maiores ganhos são M'Boi Mirim (+204), Santo Amaro (+193) e Aricanduva-Formosa-Carrão (+176).
- Por região às 17h: Oeste 0,73 e Centro 0,63 contra Norte 0,42 e Leste 0,46; depois, todas em ~0,52–0,53 com 1.057 ônibus realocados.
- Sem o piso (regra pura) às 17h: 1.649 realocados e ocupação entre 0,52 e 0,53 em todas as subprefeituras.
- Sensibilidade: a ocupação máxima às 17h é 1,07 com C = 60, 0,80 com C = 80 e 0,64 com C = 100. O alvo não depende de C (só de proporções).

**O que estes números dizem e não dizem.**
- A redistribuição **iguala a lotação**; não reduz a espera em toda hora. Às 6h a espera média ponderada piora 0,25 min, porque os ônibus saem de áreas com muitos embarques curtos para áreas com viagens longas. É um resultado real do modelo, não um defeito do código.
- Na média da linha, **nenhuma área passa da capacidade**: "não embarcados" dá zero antes e depois. A superlotação real acontece no trecho mais carregado, que este modelo não enxerga.
- Lugares ociosos somam o mesmo antes e depois (frota e carga totais não mudam). O ganho é de distribuição.

## Validações feitas
- 9,72 mi de embarques/dia na OD 2017, na ordem de grandeza dos ~9 mi/dia que a SPTrans informava antes da pandemia.
- Coordenadas da OD caem dentro da própria zona em 99,98% dos casos (mesmo sistema de coordenadas dos polígonos).
- Pipeline determinístico: duas execuções geram arquivos idênticos. 54 testes passam (propriedades de T em vetores aleatórios, piso, caso do enunciado da MMC).
- Caso do enunciado da MMC com a mesma função: x = (12, 20, 16, 24), necessidade = (14, 19, 18, 21), soma 72 nos dois; T atinge o alvo exatamente.

## Limitações (dizer antes que perguntem)
1. **Frota reconstruída acima da cadastrada.** 15,6 mil às 6h, contra ~13,4 mil ônibus de frota total noticiados em fev/2026. O GTFS traz a programação, e a duração da viagem-modelo é uma só para o dia. A política usa só proporções; os números absolutos de frota são superestimados em ~16% ou mais.
2. **Demanda de 2017 × oferta de nov/2026.** A ocupação absoluta mistura dois anos. O alvo depende só da distribuição relativa da demanda.
3. **Hora = hora de saída da viagem.** Uma viagem de 70 min que sai às 17h conta inteira nas 17h, e os trechos depois da baldeação também.
4. **Trajeto em linha reta** e tempo a bordo incluindo espera.
5. **Espera = intervalo médio por linha ÷ 2.** Onde várias linhas servem o mesmo corredor, a espera real é menor. Vale a comparação antes × depois, não o valor absoluto.
6. **Amostra.** Entre 5h e 22h, 90% das células subprefeitura × hora têm 10 ou mais viagens amostradas; de 0h a 3h, nenhuma. A coluna `amostra_ok` marca isso. A política não deve ser lida na madrugada.
7. **GTFS de cópia pública.** O arquivo veio de um repositório de terceiros no GitHub (feed com versão 09/11/2026), porque o portal da SPTrans exige login. Trocar pelo oficial quando a conta for aprovada e rodar de novo.

## Onde está cada coisa
| Arquivo | Conteúdo |
|---|---|
| `scripts/baixar_dados.py` | baixa GTFS, zonas e distritos da OD, distritos e subprefeituras do GeoSampa (endereços travados) |
| `scripts/passo0_pipeline.py` | roda tudo e grava `data/processed/` |
| `core/config.py` | caminhos e parâmetros (capacidade, lotação-alvo, perda máxima, amostra mínima, faixas do dia) |
| `core/analytics/geo.py`, `oferta.py`, `demanda.py` | geografia, GTFS → frota, OD → embarques/carga/fluxos |
| `core/frota/redistribuicao.py`, `indicadores.py` | maior resto, alvo com piso, matriz T, verificação, indicadores |
| `tests/test_redistribuicao.py` | 54 testes |
| `core/analytics/preparo.py`, `modelo.py` | funil de limpeza da OD para os modelos; treino, limiar e avaliação da logística |
| `notebooks/01_motor_de_dados_explicado.ipynb` | tudo reexecutado e explicado: entradas, fluxo, validações, regressões e treino do modelo |
| `data/processed/redistribuicao_{subprefeitura,regiao}_hora.csv` | oferta × demanda × alvo × indicadores, por área e hora (entrada da simulação) |
| `data/processed/matriz_T_*_17h.csv` | matriz T da hora de maior carga |
| `data/processed/pressao_zona_periodo.csv` | embarques por lugar ofertado, por zona e faixa do dia (mapa do gestor) |
| `data/processed/fluxos_subprefeitura_{periodo,dia}.csv` | tabelas da `consultar_fluxo` |
| `data/processed/resumo_passo0.json` | números-resumo desta execução |

Rodar: `python scripts/baixar_od2017.py && python scripts/baixar_dados.py && python scripts/passo0_pipeline.py` e `python -m pytest tests`.

## Critérios atendidos
- **MMC Etapa 1** (lógica): reconstrução da frota por relações indiretas. **Etapa 2**: necessidade, desequilíbrio, política, matriz T, prova de conservação e não negatividade, inteiros. A entrega continua separada, com os dados do enunciado.
- **Prompt & AI critério 4**: dados da ferramenta `consultar_fluxo`. **Critério 6**: a regra de amostra mínima é o argumento do guardrail de LGPD.
- **MLAM**: nada entregue aqui. Achado para a quarta: `cd_renfa` mostra que a renda familiar foi **atribuída** (não declarada) em 56% das famílias (códigos 3 e 4). Isso precisa aparecer nas limitações do relatório e pode justificar um teste de robustez só com renda declarada.
- **Extra**: pressão por zona, tabelas por região, sensibilidade de capacidade.

## Pendências que dependem do Davi
- Avisar o professor de Prompt & AI sobre a modalidade individual até **12/11**.
- Confirmar o piso de 20% (ou outro valor) e a capacidade de 80.
- Trocar o GTFS pelo oficial quando a conta de desenvolvedor da SPTrans for aprovada.
- Registrar este uso de IA no `6_Chat_Log.txt` na parte que alimenta a ferramenta do agente.
