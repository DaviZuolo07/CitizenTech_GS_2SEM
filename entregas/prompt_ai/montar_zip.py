"""Monta GS2026_2_1CCPK_LinhaCerta.zip com os 7 itens da entrega de Prompt & AI.

Uso (nesta pasta):  python montar_zip.py
Recusa montar o ZIP se faltar item, se houver campo por preencher ou se aparecer algo parecido com chave de API.
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
PRINTS = ["01_chunking", "02_busca", "03_rag", "04_agente", "05_gradio", "06_escopo",
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

nb_path = AQUI / "1_Notebook_GS2026_2.ipynb"
if nb_path.exists():
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    codigo = [c for c in nb["cells"] if c["cell_type"] == "code"]
    if any(o.get("output_type") == "error" for c in codigo for o in c.get("outputs", [])):
        problemas.append("o notebook tem célula com erro na saída")
    if sum(1 for c in codigo if not c.get("outputs")) > 2:
        problemas.append("o notebook parece não executado (muitas células sem saída)")
    saida_leitura = json.dumps(nb["cells"][27].get("outputs", []), ensure_ascii=False)
    if "Simples × armadilha" in saida_leitura and "foram melhor medidas" not in saida_leitura and "não há diferença" not in saida_leitura:
        problemas.append("a saída da célula 27 é da versão antiga: reexecute as células 27 a 29 no Colab e baixe o .ipynb de novo")

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
