"""Base documental OFICIAL do assistente do cidadão (aba Cidadão do app): baixa, limpa e grava em base_documental_oficial/.

Só fontes oficiais, cada uma com URL e data: Catálogo de Legislação Municipal (texto compilado, sem as redações
revogadas), páginas e comunicados da SPTrans. O Estatuto da Pessoa Idosa (planalto.gov.br bloqueia download
automático) fica como trecho fixo em base_documental_oficial/doc_03_estatuto_pessoa_idosa.md, copiado da página oficial.
Os documentos simulados continuam só no notebook entregue de Prompt & AI.
Uso: python scripts/base_oficial.py
"""
import html
import re
from datetime import date
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "base_documental_oficial"
LEG = "https://legislacao.prefeitura.sp.gov.br/"
SPT = "https://www.sptrans.com.br/"
# doc_id, título, URL, data (None = lida na própria página; tarifas: "Atualizado em 06/01/2026";
# Domingão: página do anúncio de 11/12/2023)
FONTES = [
    ("doc_01", "Decreto nº 58.639/2019 — normas do Bilhete Único (texto compilado)", LEG + "decreto-58639-de-22-de-fevereiro-de-2019", "2019-02-22"),
    ("doc_02", "Decreto nº 62.057/2022 — gratuidade a partir de 60 anos", LEG + "decreto-62057-de-14-de-dezembro-de-2022", "2022-12-14"),
    ("doc_04", "SPTrans — Tarifas vigentes", SPT + "tarifas/", "2026-01-06"),
    ("doc_05", "SPTrans — Domingão Tarifa Zero", SPT + "domingao-tarifa-zero/", "2023-12-11"),
    ("doc_06", "SPTrans — Prefeitura reorganiza linhas de ônibus da Zona Sul", SPT + "noticias/prefeitura-reorganiza-linhas-de-onibus-da-zona-sul-e-aumenta-oferta-de-lugares/", None),
    ("doc_07", "SPTrans — Estação Pedro II do Expresso Tiradentes fechada temporariamente", SPT + "noticias/estacao-pedro-ii-do-expresso-tiradentes-sera-fechada-temporariamente/", None),
    ("doc_08", "SPTrans — Criação da linha 6291/31", SPT + "noticias/sptrans-cria-linha-6291-31-inocoop-campo-limpo-term-bandeira/", None),
    ("doc_09", "SPTrans — Novo itinerário da linha N234/11", SPT + "noticias/sptrans-altera-itinerario-da-linha-n234-11-e-amplia-acesso-dos-passageiros-a-upa-jacana/", None),
    ("doc_10", "SPTrans — Prazos finais do Bilhete Único de Estudante 2026", SPT + "noticias/jornal-do-onibus-orienta-sobre-os-prazos-finais-do-bilhete-unico-de-estudante-2026/", None),
]
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
                                      "setembro", "outubro", "novembro", "dezembro"], 1)}


def limpar(t: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<del[^>]*>.*?</del>", " ", t, flags=re.S)          # redação revogada no texto compilado
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", t)
    t = re.sub(r"</t[dh]>", " | ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def legislacao(pagina: str) -> str:
    t = limpar(pagina)
    for marca in ("Temas Relacionados", "Texto Consolidado", "Detalhes da Norma"):
        if marca in t:
            t = t.split(marca, 1)[1]
            break
    return t.split("Este texto não substitui")[0].strip()


def sptrans(pagina: str) -> tuple:
    i = pagina.find('<section id="conteudo"')
    t = limpar(pagina[i:] if i >= 0 else pagina)
    t = re.split(r"\n\s*(Últimas notícias|Assessoria de imprensa)", t)[0]
    t = "\n".join(l for l in t.splitlines() if l.strip() not in ("Home", "Notícias") and not l.strip().startswith("Imagem ilustrativa"))
    m = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", t)
    data = date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))).isoformat() if m and m.group(2).lower() in MESES else None
    return t.strip(), data


def gravar(doc_id, titulo, url, data, corpo):
    nome = PASTA / f"{doc_id}.md"
    cab = f"---\ndoc_id: {doc_id}\ntitulo: {titulo}\nurl: {url}\ndata_publicacao: {data}\nacessado_em: {date.today().isoformat()}\n---\n"
    nome.write_text(cab + corpo + "\n", encoding="utf-8")
    return nome


if __name__ == "__main__":
    PASTA.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Linha Certa, projeto academico FIAP)"
    for doc_id, titulo, url, data in FONTES:
        r = s.get(url, timeout=40)
        r.raise_for_status()
        r.encoding = "utf-8"
        if url.startswith(LEG):
            corpo = legislacao(r.text)
        else:
            corpo, lida = sptrans(r.text)
            data = data or lida or "sem data na página"
        f = gravar(doc_id, titulo, url, data, corpo)
        print(f"{f.name}: {len(corpo.split())} palavras, data {data}")
