"""OVERSOUND - server di prova che simula le API che il gestionale esporrà al sito.

Avvio (Mac):
    pip3 install flask
    python3 sito_api.py                       -> API su http://127.0.0.1:5000
In un altro terminale, nella cartella del sito:
    python3 -m http.server 8000
Apri:  http://127.0.0.1:8000/index.html?api=http://127.0.0.1:5000

Nel gestionale vero queste funzioni leggeranno dal database invece che dalle liste qui sotto.
Regole che restano valide anche allora:
  - il sito riceve SOLO prodotti pubblicati sul sito (canale "Sito" o "Sito e Amazon");
  - i prezzi e il totale dell'ordine li calcola SEMPRE il gestionale, mai il sito;
  - nessuna chiave segreta (Stripe, ecc.) viene mai mandata al sito.
"""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"  # in produzione: solo il dominio del sito
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return r


def P(sku, nome, marca, cat, prezzo, stato, giac, ev=False, prima=None):
    return dict(sku=sku, nome=nome, marca=marca, categoria=cat, prezzo=prezzo, prezzo_prima=prima,
                stato=stato, giacenza=giac, in_evidenza=ev, immagine="", pubblicato_sito=True)


PRODOTTI = [
    P("CH-001", "Yamaha Pacifica 112V", "Yamaha", "chitarre", 289, "nuovo", 4, True),
    P("CH-002", "Fender Player Stratocaster", "Fender", "chitarre", 749, "nuovo", 2, True, 799),
    P("TA-001", "Roland FP-30X Piano Digitale", "Roland", "tastiere", 699, "nuovo", 3, True),
    P("AU-001", "JBL EON715 Cassa Attiva", "JBL", "audio", 549, "nuovo", 6, True, 599),
    P("LU-001", "Testa Mobile LED 150W", "Behringer", "luci", 169, "nuovo", 8, True, 199),
    P("MI-001", "Shure SM58", "Shure", "microfoni", 109, "nuovo", 12),
    P("AC-001", "Cavo XLR 10m", "Behringer", "accessori", 14, "nuovo", 40),
    P("TA-003", "Roland Juno-DS61", "Roland", "tastiere", 520, "usato", 1),
]
PRODOTTI.append({**P("XX-000", "Prodotto solo Amazon", "Demo", "audio", 99, "nuovo", 5), "pubblicato_sito": False})
CATEGORIE = [dict(id=i, nome=n) for i, n in [("chitarre", "Chitarre"), ("tastiere", "Tastiere"), ("audio", "Audio"),
                                              ("luci", "Luci"), ("microfoni", "Microfoni"), ("accessori", "Accessori")]]
SLIDE = [dict(id="chitarre", titolo="Nuovi arrivi chitarre", testo="Fender e Yamaha appena arrivate.", cta="Scopri le novità",
              tipo="foto", media_url="", link=None, prodotti=["CH-001", "CH-002"]),
         dict(id="service", titolo="Service audio video luci", testo="Allestimenti per eventi e concerti.", cta="Richiedi informazioni",
              tipo="video", media_url="", link="#/servizio/service", prodotti=[])]
RECENSIONI = [dict(sku="CH-002", autore="Marco R.", voto=5, titolo="Suono eccellente", testo="Ottima finitura, molto soddisfatto.",
                   data="2026-09-21", verificato=True, approvata=True)]
CONFIG = dict(azienda=dict(whatsapp="390000000000", email="info@oversound.it", indirizzo="Via Esempio 1, 00000 Città (XX)",
                           piva="P.IVA 00000000000",
                           orari=[["Lun – Ven", "9:00–13:00 / 15:30–19:30"], ["Sabato", "9:00–13:00"], ["Domenica", "Chiuso"]],
                           social=dict(instagram="https://instagram.com/", facebook="https://facebook.com/", tiktok="https://tiktok.com/")),
              soglia_spedizione_gratuita=199, tempi_consegna=[2, 4], categorie=CATEGORIE)
ORDINI, ALTRO = [], dict(avvisi=[], newsletter=[], recensioni_in_attesa=[])


@app.get("/api/config")
def config():
    return jsonify(CONFIG)


@app.get("/api/prodotti")
def prodotti():
    q = request.args.get("q", "").lower()
    out = [p for p in PRODOTTI if p["pubblicato_sito"]
           and (not request.args.get("categoria") or p["categoria"] == request.args["categoria"])
           and (not request.args.get("marca") or p["marca"] == request.args["marca"])
           and (not q or q in (p["nome"] + p["marca"]).lower())]
    return jsonify([{k: v for k, v in p.items() if k != "pubblicato_sito"} for p in out])


@app.get("/api/slide")
def slide():
    return jsonify(SLIDE)


@app.get("/api/recensioni")
def recensioni():
    return jsonify([{k: v for k, v in r.items() if k != "approvata"} for r in RECENSIONI if r["approvata"]])


@app.post("/api/ordini")
def nuovo_ordine():
    d = request.get_json(force=True, silent=True) or {}
    righe, totale = [], 0
    for r in d.get("righe", []):
        p = next((x for x in PRODOTTI if x["sku"] == r.get("sku") and x["pubblicato_sito"]), None)
        q = int(r.get("quantita", 0))
        if not p or q < 1 or q > p["giacenza"]:
            return jsonify(errore=f"Prodotto non disponibile: {r.get('sku')}"), 400
        righe.append(dict(sku=p["sku"], quantita=q, prezzo=p["prezzo"]))  # prezzo preso dal gestionale
        totale += p["prezzo"] * q
    if not righe or not d.get("cliente", {}).get("email"):
        return jsonify(errore="Ordine incompleto"), 400
    o = dict(numero=f"OS-{len(ORDINI) + 1:04d}", stato="in_attesa_pagamento", righe=righe, totale=totale, cliente=d["cliente"])
    ORDINI.append(o)
    # Gestionale vero: qui si crea la sessione Stripe Checkout e si restituisce url_pagamento.
    return jsonify(numero=o["numero"], totale=totale, stato=o["stato"], url_pagamento=None), 201


@app.post("/api/recensioni")
def invia_recensione():
    ALTRO["recensioni_in_attesa"].append(request.get_json(force=True, silent=True) or {})  # da approvare nel gestionale
    return jsonify(ok=True), 201


@app.post("/api/avvisi")
def avviso():
    ALTRO["avvisi"].append(request.get_json(force=True, silent=True) or {})
    return jsonify(ok=True), 201


@app.post("/api/newsletter")
def newsletter():
    ALTRO["newsletter"].append(request.get_json(force=True, silent=True) or {})
    return jsonify(ok=True), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
