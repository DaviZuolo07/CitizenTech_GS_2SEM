# Variáveis de entrada (OD 2017 — confirmadas no dicionário)

## Unidade de análise
Viagem com origem e destino no município de SP (`muni_o == 36 & muni_d == 36`).
Para o modelo de "quem depende do ônibus": viagens **a trabalho** (`motivo_d` ∈ {1,2,3}) de quem tem trabalho regular (`cd_ativi == 1`).
Pesos: `fe_via` (fator de expansão) para agregados populacionais; regressões na amostra (declarar).

## Alvo
| Variável | Definição | Uso |
|---|---|---|
| `usa_onibus` | 1 se `modoprin == 4` (ônibus/micro/perua do município de SP), senão 0 | regressão logística |
| `duracao` | minutos da viagem | regressão linear simples e múltipla; normal; testes de hipótese |

## Entradas (a sua ideia, traduzida em colunas)
| Ideia | Coluna | Tipo | Hipótese |
|---|---|---|---|
| CLT | `vinc1` → `clt = (vinc1 == 1)` | dummy | CLT ↑ P(ônibus) |
| Cargo na empresa | `ocup1` (11 grupos de ocupação) | categórica | ocupações operacionais ↑ P(ônibus); dirigentes ↓ |
| Setor | `setor1` (14 setores) | categórica | serviço/comércio ↑ |
| Mora longe do trabalho | `distancia` (m, linha reta) → `distancia_km` | quantitativa | ↑ distância ↑ P(transporte coletivo) até certo ponto |
| Tem carro | `qt_auto` | quantitativa | ↑ carros ↓↓ P(ônibus) |
| Renda | `renda_fa` (familiar mensal) | quantitativa | ↑ renda ↓ P(ônibus) |
| Horário de pico | `h_saida` → `pico = h_saida ∈ [6,8] ∪ [17,19]` | dummy/hora | distribuição temporal da demanda |
| Onde mora / onde trabalha | `zona_o`, `zona_d` (1–517), coords `co_o_x/y`, `co_d_x/y` | geográfica | matriz de fluxos |
| Idade | `idade` | quantitativa | controle |

⚠️ `duracao` **não** entra como preditor de `usa_onibus` (é consequência do modo — vazamento).

## Mapeamento para as exigências da MLAM
| Item | Variáveis |
|---|---|
| 02 Normal | `duracao` das viagens de ônibus a trabalho |
| 03 Testes Z (n=20 α=6% à esquerda; n=25 α=9% à direita) | `duracao`; μ₀ e σ = da população tratada; amostras com seed |
| 04 Bivariada | `duracao` ~ `distancia_km` |
| 05 Múltipla (≥3 quantitativas) | `duracao` ~ `distancia_km` + `renda_fa` + `qt_auto` (+ `idade`) |
| 06 Logística (≥3 quantitativas) | `usa_onibus` ~ `renda_fa` + `qt_auto` + `distancia_km` + `idade` (+ `clt`, `pico` como extras) |
| 07 Relatório | "Quem depende do ônibus em SP para trabalhar, e quando" |

## Do modelo ao produto
P(usa_onibus | perfil) × viagens expandidas por par de zonas e hora → **demanda estimada de ônibus por corredor/hora** → comparada à oferta (GTFS) → gap → política de redistribuição (lógica MMC).

## Tratamento planejado
1. Recorte SP→SP; 2. remover nulos em alvo e preditores; 3. `renda_fa` e `duracao` > 0; 4. outliers por IQR (registrar quantos); 5. derivar colunas; 6. exportar `entregas/mlam/dados/od2017_sp_trabalho.csv` + script que reproduz.
