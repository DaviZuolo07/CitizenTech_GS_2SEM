"""Monta GS2026_2_1CCPK_LinhaCerta.zip com os 7 itens da entrega de Prompt & AI.

Uso (nesta pasta):  python montar_zip.py
Recusa montar se faltar item, se houver campo por preencher, se aparecer algo parecido com chave de API
ou se o notebook entregue for de uma execução com problema conhecido.
"""
import json
import pathlib
import re
import sys
import zipfile

AQUI = pathlib.Path(__file__).resolve().parent
NOME_ZIP = "GS2026_2_1CCPK_LinhaCerta.zip"
ITENS = ["1_Notebook_GS2026_2.ipynb", "2_base_documental", "3_avaliacao_ragas.json", "4_README.md",
         "5_certificacao.txt", "6_Chat_Log.txt", "7_demo_video_url.txt", "prints"]
PRINTS = ["01_chunking", "02_busca", "03_rag", "04_agente", "05_interface_gradio", "06_escopo",
          "07_injection", "08_lgpd", "09_confianca", "10_ragas"]
CHAVE = re.compile(r"gsk_[A-Za-z0-9]{10,}|AIza[0-9A-Za-z_-]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|csk-[a-z0-9]{10,}|nvapi-[A-Za-z0-9_-]{10,}")
PENDENTE = re.compile(r"\[colar|\[preencher|# preencher|\[copiar")

problemas = []
for item in ITENS:
    if not (AQUI / item).exists():
        problemas.append(f"falta {item}")
for p in PRINTS:
    if not (AQUI / "prints" / f"{p}.png").exists():
        problemas.append(f"falta prints/{p}.png")

arquivos = [f for item in ITENS if (AQUI / item).exists()
            for f in ([AQUI / item] if (AQUI / item).is_file() else sorted((AQUI / item).rglob("*"))) if f.is_file()]
for f in arquivos:
    if f.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        continue
    texto = f.read_text(encoding="utf-8", errors="ignore")
    if CHAVE.search(texto):
        problemas.append(f"possível chave de API em {f.relative_to(AQUI)}")
    if f.suffix != ".ipynb" and PENDENTE.search(texto):
        problemas.append(f"campo por preencher em {f.relative_to(AQUI)}: {PENDENTE.search(texto).group(0)}...")

video = (AQUI / "7_demo_video_url.txt")
if video.exists() and not re.search(r"https://(www\.)?(youtube\.com|youtu\.be)/", video.read_text(encoding="utf-8")):
    problemas.append("7_demo_video_url.txt sem link do YouTube")


def saida(celula: dict) -> str:
    """Todo o texto que a célula imprimiu ou exibiu."""
    partes = []
    for o in celula.get("outputs", []):
        partes.append("".join(o.get("text", "")))
        for campo in ("text/markdown", "text/plain"):
            partes.append("".join(o.get("data", {}).get(campo, "")))
    return "\n".join(partes)


nb_path = AQUI / "1_Notebook_GS2026_2.ipynb"
if nb_path.exists():
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    codigo = [c for c in nb["cells"] if c["cell_type"] == "code"]
    if any(o.get("output_type") == "error" for c in codigo for o in c.get("outputs", [])):
        problemas.append("o notebook tem célula com erro na saída")
    if sum(1 for c in codigo if not c.get("outputs")) > 3:
        problemas.append("o notebook parece não executado (muitas células sem saída)")

    # As células são localizadas pelo conteúdo: a posição muda quando se acrescenta uma célula.
    leitura = [c for c in codigo if "Simples × armadilha" in "".join(c["source"])]
    if not leitura:
        problemas.append("não achei a célula da leitura dos números (seção 7)")
    elif "FRASE_NIVEL" not in "".join(leitura[0]["source"]):
        problemas.append("a célula da leitura dos números está sem a correção da frase 'simples × armadilha'")
    elif not re.search(r"foram melhor medidas|não há diferença relevante", saida(leitura[0])):
        problemas.append("a saída da leitura dos números é de uma execução anterior à correção: rode a seção 7 de novo")

    indexacao = [c for c in codigo if "def indexar" in "".join(c["source"])]
    if indexacao and "delete_collection" not in "".join(indexacao[0]["source"]):
        problemas.append("a célula de indexação está sem o delete_collection: o índice duplica se a célula rodar duas vezes")

    # A armadilha principal: a resposta do domingo tem de citar a portaria (doc_03), não só a tabela antiga.
    rag = [c for c in codigo if "NAO_SEI" in "".join(c["source"]) and "ChatPromptTemplate" in "".join(c["source"])]
    if rag:
        blocos = saida(rag[0]).split("PERGUNTA:")
        domingo = [b for b in blocos if "passa no domingo" in b]
        if domingo and "doc_03" not in domingo[0]:
            problemas.append("na seção 3 a resposta sobre o domingo não cita o doc_03: o índice provavelmente duplicou "
                             "(rode com 'Desconectar e excluir ambiente' antes de 'Executar tudo')")

if problemas:
    print("ZIP NÃO montado:")
    print("\n".join(f"  - {p}" for p in problemas))
    sys.exit(1)

destino = AQUI / NOME_ZIP
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
    for f in arquivos:
        if "__pycache__" in f.parts or f.name.startswith("."):
            continue
        z.write(f, f.relative_to(AQUI).as_posix())
print(f"ZIP montado: {destino}")
with zipfile.ZipFile(destino) as z:
    for n in z.namelist():
        print("  ", n)
