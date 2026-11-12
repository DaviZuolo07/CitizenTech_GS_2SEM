# Simulação 3D — um dia na cidade, sem e com o Linha Certa

Abra `linha_certa_simulacao.html` com dois cliques (Chrome, Edge ou Firefox). É um arquivo único, funciona sem internet.

## O que mostra
Duas cópias da mesma cidade fictícia, lado a lado, com a mesma demanda (mesmas chegadas, mesma semente) e os mesmos 36 ônibus:
- **Sem Linha Certa:** frota fixa por bairro, proporcional à população, o dia inteiro.
- **Com Linha Certa:** a cada hora a frota é redistribuída pela regra do produto.

Controles: pausar, velocidade 1×/3×/8×, reiniciar; arrastar gira a câmera e a rolagem aproxima. O botão "Modelo e frota" abre a tabela com a probabilidade de usar ônibus de cada bairro e as realocações da hora. Um dia (5h às 23h) leva 90 segundos em 1×.

## O que é real e o que é fictício
| Elemento | Origem |
|---|---|
| P(usa ônibus) de cada bairro | **real**: coeficientes da regressão logística treinada na Pesquisa OD 2017 (`src/sim.js`, `MODELO`) |
| Forma da demanda ao longo do dia | **real**: embarques de ônibus por hora na OD 2017 (`EMBARQUES_HORA`) |
| Regra de redistribuição | **real**: a mesma de `core/frota/redistribuicao.py` (maior resto, piso de 20% por hora, matriz T), reescrita em JavaScript e conferida contra o Python |
| Cidade, bairros, população, renda, distâncias, frota, capacidade | **fictícios**, escolhidos para caber na tela |
| Custo por km (R$ 10) | **parâmetro ilustrativo**, não é dado |

## Resultado desta configuração
Espera média de 11,1 para 6,8 min (−38%); maior fila de 219 para 90 pessoas; mesma quilometragem. Para chegar a essa espera sem redistribuir, a operação fixa precisaria de 44 ônibus (8 a mais).

**Leitura correta:** a simulação mostra que a regra funciona numa cidade pequena e controlada. Não prova o ganho em São Paulo; os números da cidade real estão em `docs/08_modelo_produto.md`.

## Arquivos
- `linha_certa_simulacao.html` — a simulação pronta (Three.js embutido).
- `src/sim.js` — lógica (modelo, demanda, ônibus, filas, redistribuição), sem nada de tela.
- `src/main.js` — cena 3D e painel. `modelo.html` — página e estilos.
- `teste_sim.mjs` — testes da lógica: `node teste_sim.mjs`.

## Para alterar e reempacotar
```
npm install three@0.160.0 esbuild@0.21.5
npx esbuild src/main.js --bundle --minify --format=iife --outfile=bundle.js
```
Depois, cole o conteúdo de `bundle.js` no lugar de `/*BUNDLE*/` em `modelo.html` e salve como `linha_certa_simulacao.html`. Os parâmetros da cidade ficam no topo de `src/sim.js` (`BAIRROS` e `P`).
