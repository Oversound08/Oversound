"""Crea una pagina vera per ogni prodotto del sito (oversound.it/prodotto/nome-prodotto/) e la mappa del sito.

Google legge bene solo gli indirizzi «veri», non quelli con # (es. oversound.it/#/prodotto/...).
Questo programma prende i prodotti dal gestionale e per ognuno scrive una copia del sito con titolo,
descrizione, foto, prezzo e dati strutturati già dentro: Google la trova, il cliente vede il sito normale.
Lo fa da solo GitHub ogni 6 ore (.github/workflows/pagine-seo.yml). A mano:  python3 strumenti/genera_pagine.py
"""
import html, json, os, re, shutil, sys, time, unicodedata, urllib.parse, urllib.request
from datetime import date

API = os.environ.get("API_URL", "https://oversound.pythonanywhere.com").rstrip("/")
SITO = "https://oversound.it"
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CART = os.path.join(QUI, "prodotto")
CARTC = os.path.join(QUI, "categoria")
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


def slug_cat(t):
    t = unicodedata.normalize("NFD", str(t or "").lower()); t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:80]


GIORNI = {"lun": "Mo", "mar": "Tu", "mer": "We", "gio": "Th", "ven": "Fr", "sab": "Sa", "dom": "Su"}


def orari_schema(orari):
    """«Lunedì – Venerdì | 9:00 – 13:00 / 15:30 – 19:30» -> ["Mo-Fr 09:00-13:00", "Mo-Fr 15:30-19:30"]"""
    out = []
    for r in orari or []:
        if not isinstance(r, (list, tuple)) or len(r) < 2 or re.search(r"chius", str(r[1]), re.I): continue
        g = [GIORNI.get(x[:3].lower().replace("ì", "i")) for x in re.findall(r"[A-Za-zÀ-ú]+", str(r[0])) if x[:3].lower().replace("ì", "i") in GIORNI]
        if not g: continue
        gg = g[0] if len(g) == 1 else f"{g[0]}-{g[-1]}" if re.search(r"[–-]", str(r[0])) else ",".join(g)
        for a, b, c, d in re.findall(r"(\d{1,2})[:.](\d{2})\s*[–-]\s*(\d{1,2})[:.](\d{2})", str(r[1])): out.append(f"{gg} {int(a):02d}:{b}-{int(c):02d}:{d}")
    return out


def negozio(az):
    """Scheda del negozio per Google (MusicStore) con i dati del gestionale."""
    ind = str(az.get("indirizzo") or ""); j = {"@context": "https://schema.org", "@type": "MusicStore", "@id": SITO + "/#negozio", "name": "OVERSOUND",
        "alternateName": "OVERSOUND Damiano Perri – Strumenti musicali", "url": SITO + "/", "logo": SITO + "/icone/app-512.png", "image": SITO + "/icone/logo.webp", "priceRange": "€€"}
    m = re.match(r"\s*(.+?),\s*(\d{5})\s+(.+?)(?:\s*\((\w{2})\))?\s*$", ind)
    if m and not re.search(r"esempio", ind, re.I):
        j["address"] = {"@type": "PostalAddress", "streetAddress": m.group(1), "postalCode": m.group(2), "addressLocality": m.group(3).strip(), "addressCountry": "IT"}
        if m.group(4): j["address"]["addressRegion"] = m.group(4)
    elif ind and not re.search(r"esempio", ind, re.I): j["address"] = ind
    if az.get("whatsapp"): j["telephone"] = "+" + re.sub(r"\D", "", str(az["whatsapp"]))
    if az.get("email"): j["email"] = az["email"]
    oh = orari_schema(az.get("orari"))
    if oh: j["openingHours"] = oh
    so = [u for u in (az.get("social") or {}).values() if u and not re.fullmatch(r"https://(www\.)?(instagram|facebook|tiktok)\.com/?", u)]
    if so: j["sameAs"] = so
    return j


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
        {"@type": "ListItem", "position": 2, "name": p.get("categoria") or "Catalogo", "item": f"{SITO}/categoria/{slug_cat(p.get('categoria'))}/" if slug_cat(p.get("categoria")) else SITO + "/"},
        {"@type": "ListItem", "position": 3, "name": nome, "item": url}]}
    t = tpl
    t = re.sub(r"<title>.*?</title>", f"<title>{E(tit)}</title>", t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', t, count=1)
    t = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{E(url)}">', t, count=1)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(tit)}">', t, count=1)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', t, count=1)
    t = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{E(url)}">', t, count=1)
    t = t.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="product">', 1)
    t = t.replace('<meta property="og:image" content="https://oversound.it/icone/app-512.png">', f'<meta property="og:image" content="{E(foto[0])}">' if foto else '<meta property="og:image" content="https://oversound.it/icone/app-512.png">', 1)
    testa = ('<base href="/">'
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


def pagina_categoria(tpl, cat, prodotti, az):
    sl = slug_cat(cat); url = f"{SITO}/categoria/{sl}/"
    tit = f"{cat} – negozio e vendita online | OVERSOUND"
    marche = sorted({p.get("marca") for p in prodotti if p.get("marca")})[:6]
    desc = (f"{cat} da OVERSOUND, negozio di strumenti musicali: {len(prodotti)} prodotti" + (f" ({', '.join(marche)})" if marche else "") + ". Spedizione in Italia o ritiro in negozio.")[:160]
    lista = {"@context": "https://schema.org", "@type": "ItemList", "name": cat, "numberOfItems": len(prodotti),
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITO}/prodotto/{p['slug']}/", "name": p["nome"]} for i, p in enumerate(prodotti[:100])]}
    bric = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITO + "/"}, {"@type": "ListItem", "position": 2, "name": cat, "item": url}]}
    t = tpl
    t = re.sub(r"<title>.*?</title>", f"<title>{E(tit)}</title>", t, count=1, flags=re.S)
    for pat, val in ((r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">'), (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{E(url)}">'),
                     (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(tit)}">'), (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">'),
                     (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{E(url)}">')): t = re.sub(pat, lambda _, v=val: v, t, count=1)
    t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8"><base href="/">' + f'<script>window.OS_ROUTE={js("/catalogo?cat=" + urllib.parse.quote(cat))}</script>'
                  + f'<script type="application/ld+json">{js(lista)}</script><script type="application/ld+json">{js(bric)}</script>', 1)
    righe = "".join(f'<li style="margin:6px 0"><a href="/prodotto/{E(p["slug"])}/" style="color:#111">{E(p["nome"])}</a> <b>{euro(float(p.get("prezzo") or 0))}</b></li>' for p in prodotti[:200])
    corpo = (f'<div id="root"><main style="max-width:760px;margin:0 auto;padding:24px 16px;font-family:system-ui,sans-serif;color:#111"><a href="/"><img src="/icone/logo.webp" alt="OVERSOUND" width="900" height="196" style="width:220px;height:auto"></a>'
             f'<h1 style="font-size:28px">{E(cat)}</h1><p>{E(desc)}</p><ul style="padding-left:18px">{righe}</ul></main></div>')
    t2 = re.sub(r'<div id="root">.*?</div></div>', lambda _: corpo, t, count=1, flags=re.S)
    return t2


def scrivi(f, testo):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    if not os.path.exists(f) or open(f, encoding="utf-8").read() != testo: open(f, "w", encoding="utf-8").write(testo); return True
    return False


def main():
    try:
        lista = leggi("/api/lista"); az = (leggi("/api/vetrina") or {}).get("azienda", {})
    except Exception as ex:
        print("Gestionale non raggiungibile, non cambio niente:", ex); return 0
    if not isinstance(lista, list) or not lista:
        print("Nessun prodotto dal gestionale: non cambio niente."); return 0
    # scheda del negozio (indirizzo, orari, contatti) anche nella pagina principale
    fi = os.path.join(QUI, "index.html"); tpl = open(fi, encoding="utf-8").read()
    blocco = f'<!--NEGOZIO--><script type="application/ld+json" id="ld-negozio-fisso">{js(negozio(az))}</script><!--/NEGOZIO-->'
    tpl = re.sub(r"<!--NEGOZIO-->.*?<!--/NEGOZIO-->", lambda _: blocco, tpl, count=1, flags=re.S)
    scrivi(fi, tpl)
    fatti = set(); percat = {}
    for p in lista:
        slug = str(p.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,99}", slug) or not p.get("codice"): continue
        try: d = leggi("/api/prodotto/" + urllib.parse.quote(slug), prove=2)
        except Exception: d = {}
        scrivi(os.path.join(CART, slug, "index.html"), pagina(tpl, p, d if isinstance(d, dict) else {}, az))
        fatti.add(slug)
        if p.get("categoria"): percat.setdefault(p["categoria"], []).append(p)
    cats = set()
    for cat, P in percat.items():
        sl = slug_cat(cat)
        if not sl or sl in cats: continue
        scrivi(os.path.join(CARTC, sl, "index.html"), pagina_categoria(tpl, cat, sorted(P, key=lambda x: x["nome"].lower()), az)); cats.add(sl)
    for cart, tenere in ((CART, fatti), (CARTC, cats)):   # prodotti e categorie tolti dal sito: via anche la pagina
        if os.path.isdir(cart):
            for x in os.listdir(cart):
                if x not in tenere and os.path.isdir(os.path.join(cart, x)): shutil.rmtree(os.path.join(cart, x))
    url = [SITO + "/"] + [f"{SITO}/categoria/{s}/" for s in sorted(cats)] + [f"{SITO}/prodotto/{s}/" for s in sorted(fatti)]
    scrivi(os.path.join(QUI, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(f"<url><loc>{html.escape(u)}</loc></url>\n" for u in url) + "</urlset>\n")
    print(f"Pagine: {len(fatti)} prodotti, {len(cats)} categorie. Mappa del sito: {len(url)} indirizzi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
