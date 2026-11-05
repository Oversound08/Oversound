"""Crea una pagina vera per ogni prodotto del sito (oversound.it/prodotto/nome-prodotto/) e la mappa del sito.

Google legge bene solo gli indirizzi «veri», non quelli con # (es. oversound.it/#/prodotto/...).
Questo programma prende i prodotti dal gestionale e per ognuno scrive una copia del sito con titolo,
descrizione, foto, prezzo e dati strutturati già dentro: Google la trova, il cliente vede il sito normale.
Lo fa da solo GitHub ogni 6 ore (.github/workflows/pagine-seo.yml). A mano:  python3 strumenti/genera_pagine.py
"""
import html, json, os, re, shutil, sys, time, urllib.parse, urllib.request
from datetime import date

API = os.environ.get("API_URL", "https://oversound.pythonanywhere.com").rstrip("/")
SITO = "https://oversound.it"
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CART = os.path.join(QUI, "prodotto")
E = lambda t: html.escape(str(t or ""), quote=True)


def leggi(percorso, prove=3):
    for k in range(prove):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + percorso, headers={"User-Agent": "OVERSOUND-pagine-seo"}), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as ex:
            if k == prove - 1: raise
            time.sleep(3 + 5 * k)


def euro(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def js(o): return json.dumps(o, ensure_ascii=False).replace("</", "<\\/")


def pagina(tpl, p, d, az):
    sku, slug = p["codice"], p["slug"]; url = f"{SITO}/prodotto/{slug}/"
    nome = p["nome"]; marca = p.get("marca") or ""
    foto = [f["url"] for f in (d.get("foto") or p.get("foto") or []) if f.get("url")][:8]
    breve = (d.get("descrizione_breve") or re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", d.get("descrizione") or "")).strip() or "")[:300]
    tit = d.get("seo_titolo") or f"{nome} | OVERSOUND"
    desc = breve[:160] or f"{(marca + ' ') if marca and marca.lower() not in nome.lower() else ''}{nome}: disponibile su OVERSOUND, strumenti musicali, audio e luci."
    prezzo = float(p.get("prezzo") or 0); disp = p.get("disponibile")
    prod = {"@context": "https://schema.org", "@type": "Product", "name": nome, "sku": sku, "url": url,
            "offers": {"@type": "Offer", "url": url, "price": f"{prezzo:.2f}", "priceCurrency": "EUR",
                       "availability": "https://schema.org/" + ("InStock" if disp else "OutOfStock"),
                       "itemCondition": "https://schema.org/" + ("UsedCondition" if p.get("usato") else "NewCondition"),
                       "seller": {"@type": "Organization", "name": "OVERSOUND", "url": SITO + "/"}}}
    if foto: prod["image"] = foto
    if marca: prod["brand"] = {"@type": "Brand", "name": marca}
    if breve: prod["description"] = breve
    if re.fullmatch(r"\d{8,14}", str(d.get("ean") or "")): prod["gtin"] = d["ean"]
    briciole = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITO + "/"},
        {"@type": "ListItem", "position": 2, "name": p.get("categoria") or "Catalogo", "item": SITO + "/#/catalogo?cat=" + urllib.parse.quote(p.get("categoria") or "")},
        {"@type": "ListItem", "position": 3, "name": nome, "item": url}]}
    t = tpl
    t = re.sub(r"<title>.*?</title>", f"<title>{E(tit)}</title>", t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', t, count=1)
    t = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{E(url)}">', t, count=1)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(tit)}">', t, count=1)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', t, count=1)
    t = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{E(url)}">', t, count=1)
    t = t.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="product">', 1)
    testa = (f'<base href="/">' + (f'<meta property="og:image" content="{E(foto[0])}">' if foto else "")
             + f'<script>window.OS_ROUTE={js("/prodotto/" + sku)}</script>'
             + f'<script type="application/ld+json" id="ld-prodotto">{js(prod)}</script><script type="application/ld+json">{js(briciole)}</script>')
    t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + testa, 1)
    # contenuto visibile subito (anche a chi non esegue JavaScript); il sito lo sostituisce appena è pronto
    corpo = (f'<div id="root"><main style="max-width:760px;margin:0 auto;padding:24px 16px;font-family:system-ui,sans-serif;color:#111">'
             f'<a href="/"><img src="/icone/logo.webp" alt="OVERSOUND" width="900" height="196" style="width:220px;height:auto"></a>'
             + (f'<img src="{E(foto[0])}" alt="{E(nome)}" style="display:block;width:100%;max-width:480px;aspect-ratio:1;object-fit:contain;margin:20px 0;background:#f6f6f7;border-radius:16px">' if foto else "")
             + f'<p style="color:#666;margin:16px 0 4px">{E(marca)}</p><h1 style="font-size:28px;margin:0 0 8px">{E(nome)}</h1>'
             f'<p style="font-size:24px;font-weight:800;margin:0 0 12px">{euro(prezzo)}</p><p>{E(breve)}</p>'
             f'<p><a href="/#/prodotto/{E(urllib.parse.quote(sku))}" style="display:inline-block;background:#e10600;color:#fff;padding:12px 22px;border-radius:99px;text-decoration:none;font-weight:700">Vedi il prodotto</a></p></main></div>')
    t2 = re.sub(r'<div id="root">.*?</div></div>', lambda _: corpo, t, count=1, flags=re.S)
    if t2 == t: raise SystemExit("Non trovo il contenitore del sito in index.html")
    return t2


def main():
    tpl = open(os.path.join(QUI, "index.html"), encoding="utf-8").read()
    try:
        lista = leggi("/api/lista"); az = (leggi("/api/vetrina") or {}).get("azienda", {})
    except Exception as ex:
        print("Gestionale non raggiungibile, non cambio niente:", ex); return 0
    if not isinstance(lista, list) or not lista:
        print("Nessun prodotto dal gestionale: non cambio niente."); return 0
    fatti = set(); os.makedirs(CART, exist_ok=True)
    for p in lista:
        slug = str(p.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,99}", slug) or not p.get("codice"): continue
        try: d = leggi("/api/prodotto/" + urllib.parse.quote(slug), prove=2)
        except Exception: d = {}
        out = pagina(tpl, p, d if isinstance(d, dict) else {}, az)
        os.makedirs(os.path.join(CART, slug), exist_ok=True)
        f = os.path.join(CART, slug, "index.html")
        if not os.path.exists(f) or open(f, encoding="utf-8").read() != out:
            open(f, "w", encoding="utf-8").write(out)
        fatti.add(slug)
    for x in os.listdir(CART):   # prodotti tolti dal sito: via anche la pagina
        if x not in fatti and os.path.isdir(os.path.join(CART, x)): shutil.rmtree(os.path.join(CART, x))
    url = [SITO + "/"] + [f"{SITO}/prodotto/{s}/" for s in sorted(fatti)]
    open(os.path.join(QUI, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{html.escape(u)}</loc></url>\n" for u in url) + "</urlset>\n")
    print(f"Pagine dei prodotti: {len(fatti)}. Mappa del sito: {len(url)} indirizzi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
