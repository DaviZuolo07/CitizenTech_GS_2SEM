# App local — frota ao vivo (API Olho Vivo)

Mapa de São Paulo com a posição de todos os ônibus em operação, atualizado a cada 20 s.

## Rodar
1. Na raiz do repositório, crie o arquivo `.env` com uma linha: `OLHOVIVO_TOKEN=seu_token`. O `.env` está no `.gitignore`.
2. `pip install requests`
3. `python app/servidor.py`
4. Abra http://localhost:8000

## Por que existe um servidor
A API Olho Vivo autentica por cookie de sessão e não aceita chamadas diretas do navegador. E o token não pode ir para o navegador. O `servidor.py` autentica uma vez, guarda a sessão, faz cache de 15 s e entrega ao navegador só os dados.

## Rotas
| Rota | O que devolve |
|---|---|
| `/api/posicao` | todos os veículos: linha, sentido, letreiros, prefixo, latitude, longitude, hora da posição |
| `/api/empresas` | empresas operadoras por área (endpoint `/Empresa`) |
| `/api/linhas?termo=8000` | busca de linhas |
| `/api/previsao?parada=CODIGO` | chegada prevista dos ônibus numa parada |
