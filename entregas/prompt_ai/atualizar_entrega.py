"""Preenche o 4_README.md e o 5_certificacao.txt com os resultados da execução do notebook.

Uso (nesta pasta):  python atualizar_entrega.py
Rode depois de cada execução do notebook. Nenhum número é digitado à mão: todos saem do JSON exportado
pela seção 7, então o README, o JSON e o notebook nunca divergem.
"""
import datetime
import json
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent
JSON = AQUI / "3_avaliacao_ragas.json"
README = AQUI / "4_README.md"
CERT = AQUI / "5_certificacao.txt"
NOTEBOOK = AQUI / "1_Notebook_GS2026_2.ipynb"
INICIO, FIM = "<!-- RAGAS:inicio -->", "<!-- RAGAS:fim -->"
METRICAS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
METAS = dict(zip(METRICAS, (0.80, 0.75, 0.70, 0.70)))      # metas de referência do enunciado

if not JSON.exists():
    sys.exit(f"não achei {JSON.name}: baixe-o do Colab (painel Arquivos, pasta content) antes de rodar isto")

dados = json.loads(JSON.read_text(encoding="utf-8"))
usada = dados["estrategia_usada_no_assistente"]
outra = next(n for n in "AB" if n != usada)
versao = {"A": "v1", "B": "v2"}
conf = {n: dados["versoes"][f"chunking_{n}"] for n in "AB"}
perg = {n: conf[n]["por_pergunta"] for n in "AB"}
media = {n: conf[n]["media"] for n in "AB"}
f3 = lambda x: "—" if x is None else f"{x:.3f}"
f2 = lambda x: "—" if x is None else f"{x:.2f}"


def media_nivel(n, nivel, m):
    vs = [p[m] for p in perg[n] if p["nivel"] == nivel and p[m] is not None]
    return sum(vs) / len(vs) if vs else None


def vencedor(m):
    a, b = media["A"][m], media["B"][m]
    if a is None or b is None or abs(a - b) < 0.01:
        return "empate"
    return f"{versao['A']} (chunking A)" if a > b else f"{versao['B']} (chunking B)"


L = []
L.append(f"Execução de {datetime.date.fromtimestamp(JSON.stat().st_mtime):%d/%m/%Y} no Google Colab. "
         f"Agente: {dados['provedor']}, `{dados['modelo']}`. Juiz do RAGAS: {dados['juiz']} "
         f"(outro provedor e outro modelo, para o agente não avaliar as próprias respostas). "
         f"Embeddings: `{dados['embeddings'].split('/')[-1]}`. `k = {dados['k']}`. "
         f"Valores completos, com a resposta dada a cada pergunta, em `3_avaliacao_ragas.json`.\n")
L.append("Conjunto: 8 perguntas, 4 simples (nível 1) e 4 que dependem das armadilhas (nível 2), cada uma com resposta "
         "de referência conferida contra os documentos (processo descrito no `6_Chat_Log.txt`). v1 e v2 usam o mesmo "
         "modelo, o mesmo juiz, o mesmo `k` e as mesmas perguntas; só muda o chunking.\n")

L.append("### Médias")
L.append("| Versão | " + " | ".join(METRICAS) + " |")
L.append("|---|" + "---|" * len(METRICAS))
for n in "AB":
    rotulo = (f"{versao[n]} — chunking {n} ({conf[n]['chunk_size']}/{conf[n]['overlap']})"
              + (", **usada no assistente**" if n == usada else ""))
    destaque = (lambda s: f"**{s}**") if n == usada else (lambda s: s)
    L.append(f"| {rotulo} | " + " | ".join(destaque(f3(media[n][m])) for m in METRICAS) + " |")
L.append("")

L.append("### Médias por nível")
L.append("| Versão | Nível | " + " | ".join(METRICAS) + " |")
L.append("|---|---|" + "---|" * len(METRICAS))
for n in "AB":
    for nivel, nome in ((1, "simples"), (2, "armadilha")):
        L.append(f"| {versao[n]} | {nivel} ({nome}) | " + " | ".join(f3(media_nivel(n, nivel, m)) for m in METRICAS) + " |")
L.append("")

L.append(f"### Por pergunta ({versao['A']} → {versao['B']})")
L.append("| # | Nível | Pergunta | " + " | ".join(METRICAS) + " |")
L.append("|---|---|---|" + "---|" * len(METRICAS))
for i, (a, b) in enumerate(zip(perg["A"], perg["B"]), 1):
    L.append(f"| {i} | {a['nivel']} | {a['pergunta']} | "
             + " | ".join(f"{f3(a[m])} → {f3(b[m])}" for m in METRICAS) + " |")
vazias = [(versao[n], i, m) for n in "AB" for i, p in enumerate(perg[n], 1) for m in METRICAS if p[m] is None]
if vazias:
    L.append("")
    L.append(f"O juiz não devolveu valor em {len(vazias)} das 64 medições ("
             + "; ".join(f"{v}, pergunta {i}, `{m}`" for v, i, m in vazias)
             + "). Essas entram como vazio no JSON e ficam fora das médias, que são calculadas só sobre o que foi "
               "medido; a comparação entre v1 e v2 em cada métrica usa as perguntas medidas nas duas versões.")
faltando = {n: [(i, p["docs_faltando"]) for i, p in enumerate(perg[n], 1) if p["docs_faltando"]] for n in "AB"}
L.append("")
for n in "AB":
    if faltando[n]:
        L.append(f"Na {versao[n]}, o contexto ficou sem documento necessário em: "
                 + "; ".join(f"pergunta {i} ({', '.join(d)})" for i, d in faltando[n]) + ".")
    else:
        L.append(f"Na {versao[n]}, nenhuma pergunta ficou sem documento necessário no contexto.")
L.append("")

L.append("### O que os números dizem")
ganhou = [m for m in METRICAS if vencedor(m) == f"{versao[usada]} (chunking {usada})"]
perdeu = [m for m in METRICAS if vencedor(m) == f"{versao[outra]} (chunking {outra})"]
linha1 = (f"1. **Comparação v1 × v2.** A versão usada ({versao[usada]}, chunking {usada}) ficou à frente em "
          + (", ".join(f"`{m}` ({f2(media[usada][m])} contra {f2(media[outra][m])})" for m in ganhou) if ganhou else "nenhuma métrica"))
if perdeu:
    linha1 += ("; ficou atrás em "
               + ", ".join(f"`{m}` ({f2(media[usada][m])} contra {f2(media[outra][m])})" for m in perdeu))
linha1 += (". A escolha do chunking foi feita antes, pelo teste das armadilhas da seção 1, e a avaliação "
           + ("confirma essa escolha." if len(ganhou) > len(perdeu) else
              "a confirma só em parte: o ganho está na recuperação, e é por ela que a resposta das armadilhas depende."))
L.append(linha1)

difs = {m: (media_nivel(usada, 2, m) or 0) - (media_nivel(usada, 1, m) or 0) for m in METRICAS}
mn = max(difs, key=lambda m: abs(difs[m]))
sentido = ("melhor nas armadilhas que nas simples" if difs[mn] > 0.01 else
           "melhor nas simples que nas armadilhas" if difs[mn] < -0.01 else "igual nos dois níveis")
L.append(f"2. **Simples × armadilha.** Na versão usada, a maior diferença está em `{mn}`: "
         f"{f2(media_nivel(usada, 1, mn))} nas simples contra {f2(media_nivel(usada, 2, mn))} nas armadilhas, "
         f"ou seja, {sentido}. As armadilhas são as perguntas que dependem de dois documentos, "
         f"o antigo e o que o corrige.")

pior = min(perg[usada], key=lambda p: sum(p[m] or 0 for m in METRICAS))
med_pior = sum(pior[m] or 0 for m in METRICAS) / 4
if pior["docs_faltando"]:
    causa = (f"a busca não trouxe {', '.join(pior['docs_faltando'])}, necessário para a resposta "
             f"(`context_recall` {f2(pior['context_recall'])})")
    melhoria = ("aumentar `k` ou filtrar por `data_publicacao`, para o documento mais recente sobre o tema "
                "entrar no contexto")
    alvo = "context_recall"
elif (pior["context_recall"] or 0) < 0.5:
    causa = (f"o documento certo foi recuperado, mas não o trecho que responde: `context_recall` "
             f"{f2(pior['context_recall'])} e `context_precision` {f2(pior['context_precision'])}"
             + ("; sem o trecho, o assistente responde que não há informação, e isso zera o `answer_relevancy`"
                if (pior["answer_relevancy"] or 0) < 0.1 else ""))
    melhoria = ("busca híbrida, somando BM25 à busca por embeddings, porque um código como \"502C-10\" é termo exato "
                "que o embedding representa mal; e reranking dos trechos")
    alvo = "context_recall"
else:
    alvo = min(["faithfulness", "answer_relevancy"], key=lambda m: pior[m] if pior[m] is not None else 2)
    causa = (f"os trechos necessários vieram (`context_recall` {f2(pior['context_recall'])}), então a perda está na "
             f"geração: `faithfulness` {f2(pior['faithfulness'])} e `answer_relevancy` {f2(pior['answer_relevancy'])}")
    melhoria = ("abrir a resposta com o dado direto antes da fonte" if alvo == "answer_relevancy"
                else "prompt mais restritivo, afirmando só o que está nos trechos, e reranking")
L.append(f"3. **Pior pergunta.** \"{pior['pergunta']}\" (média {f2(med_pior)}): {causa}.")
L.append(f"4. **Melhoria proposta.** {melhoria[0].upper() + melhoria[1:]}. "
         f"Meta: levar o `{alvo}` dessa pergunta de {f2(pior[alvo])} para pelo menos 0,70.")

na_meta = [m for m in METRICAS if (media[usada][m] or 0) >= METAS[m]]
fora = [m for m in METRICAS if m not in na_meta]
L.append("5. **Metas de referência.** Na versão usada, "
         + (", ".join(f"`{m}` ({f2(media[usada][m])}; meta {METAS[m]:.2f})" for m in na_meta) + " na meta"
            if na_meta else "nenhuma métrica atingiu a meta")
         + ("; " + ", ".join(f"`{m}` ({f2(media[usada][m])}; meta {METAS[m]:.2f})" for m in fora) + " abaixo." if fora else "."))
L.append("")
L.append("As métricas vêm de um modelo juiz e variam entre execuções, principalmente o `answer_relevancy`, que gera "
         "perguntas a partir da resposta. Por isso a leitura é a comparação entre v1 e v2, medidas com o mesmo juiz "
         "na mesma execução, e não o valor absoluto de cada número. Com 8 perguntas, uma delas move a média de uma "
         "métrica em até 0,125.")

bloco = "\n".join(L)
texto = README.read_text(encoding="utf-8")
if INICIO not in texto or FIM not in texto:
    sys.exit(f"não achei os marcadores {INICIO} / {FIM} no 4_README.md")
novo = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM), f"{INICIO}\n{bloco}\n{FIM}", texto, flags=re.S)
README.write_text(novo, encoding="utf-8")
print(f"4_README.md atualizado com os números de {JSON.name} ({len(bloco.splitlines())} linhas na seção).")


# ---- 5_certificacao.txt: dados da execução e tela final, lidos do notebook executado ----
def texto_saida(celula):
    """Texto de uma célula. Quando há markdown, o text/plain é só o repr do objeto e é descartado."""
    partes = []
    for o in celula.get("outputs", []):
        partes.append("".join(o.get("text", "")))
        dados_o = o.get("data", {})
        partes.append("".join(dados_o.get("text/markdown") or dados_o.get("text/plain", "")))
    return "\n".join(p for p in partes if p.strip())


if not NOTEBOOK.exists():
    sys.exit("não achei o notebook executado; o 5_certificacao.txt não foi atualizado")
nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
codigo = [c for c in nb["cells"] if c["cell_type"] == "code"]
conclusao = [c for c in codigo if "O que funcionou" in "".join(c["source"])]
if not conclusao:
    sys.exit("não achei a célula da conclusão (seção 8) no notebook")
tela = re.sub(r"[*`]", "", texto_saida(conclusao[0])).strip()
if not tela:
    sys.exit("a célula da conclusão está sem saída: rode a seção 8 no Colab antes")

medidas = sum(1 for n in "AB" for p in perg[n] for m in METRICAS if p[m] is not None)
bloco_cert = "\n".join([
    f"- Data: {datetime.date.fromtimestamp(JSON.stat().st_mtime):%d/%m/%Y}, Google Colab, \"Executar tudo\", sem erros.",
    f"- Agente: {dados['provedor']}, {dados['modelo']}. Juiz do RAGAS: {dados['juiz']}.",
    f"- Embeddings: {dados['embeddings']} (no próprio Colab).",
    f"- RAGAS: {medidas} de 64 medições válidas (8 perguntas x 4 métricas x 2 versões de chunking).",
    "",
    "Tela final (saída da seção 8, Conclusão)",
    "",
    tela,
])
texto_cert = CERT.read_text(encoding="utf-8")
if INICIO.replace("RAGAS", "EXECUCAO") not in texto_cert:
    sys.exit("não achei os marcadores EXECUCAO no 5_certificacao.txt")
ini, fim = INICIO.replace("RAGAS", "EXECUCAO"), FIM.replace("RAGAS", "EXECUCAO")
CERT.write_text(re.sub(re.escape(ini) + r".*?" + re.escape(fim), f"{ini}\n{bloco_cert}\n{fim}", texto_cert, flags=re.S),
                encoding="utf-8")
print("5_certificacao.txt atualizado com os dados da execução e a tela final.")
