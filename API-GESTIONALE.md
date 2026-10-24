# Contratto API: gestionale ⇄ sito OVERSOUND

Il **gestionale decide tutto**; il sito legge (e invia gli ordini) tramite questi indirizzi. Formato: JSON.
Il sito si collega all'indirizzo scritto in `API_URL` dentro `index.html` (oppure, per le prove, aggiungendo `?api=http://127.0.0.1:5000` all'indirizzo del sito).
Se il gestionale non risponde il sito mostra dati di esempio e lo segnala.

## Cosa il sito LEGGE (GET)
| Indirizzo | Contenuto |
|---|---|
| `/api/config` | `azienda` (whatsapp, email, indirizzo, piva, orari, social), `soglia_spedizione_gratuita`, `tempi_consegna` [min,max] giorni lavorativi, `categorie` [{id, nome}] |
| `/api/prodotti` | solo prodotti **pubblicati sul sito**: `sku, nome, marca, categoria, prezzo, prezzo_prima, stato` (nuovo/usato), `giacenza, in_evidenza, immagine` (indirizzo pubblico della foto). Filtri facoltativi: `?q=&categoria=&marca=` |
| `/api/slide` | `id, titolo, testo, cta, tipo` (foto/video), `media_url, link` (vuoto = pagina novità), `prodotti` [sku] |
| `/api/recensioni` | solo le **approvate**: `sku, autore, voto, titolo, testo, data, verificato` |

Corrispondenza con i campi del gestionale: `cod→sku`, `ven→prezzo`, `giac→giacenza`, `cat→categoria`, `marca→marca`; il canale (`can`) decide cosa è pubblicato: "Sito" e "Sito e Amazon" sì, "Solo Amazon" no.

## Cosa il sito INVIA (POST)
| Indirizzo | Dati | Cosa fa il gestionale |
|---|---|---|
| `/api/ordini` | `cliente` {nome, email, telefono, indirizzo}, `righe` [{sku, quantita}] | **ricalcola prezzi e totale da solo** (ignora quelli del sito), controlla la giacenza, crea l'ordine "in attesa di pagamento" e risponde con `numero` e `url_pagamento` |
| `/api/recensioni` | `sku, autore, voto, titolo, testo` | la mette in coda "da approvare" |
| `/api/avvisi` | `sku, email` | ricorda l'avviso "torna disponibile" |
| `/api/newsletter` | `email` | iscrizione |

## Ordini e pagamenti (Stripe)
1. Il sito invia l'ordine → il gestionale lo registra (stato `in_attesa_pagamento`) e crea la sessione **Stripe Checkout**; il sito porta il cliente su `url_pagamento`.
2. Stripe avvisa il gestionale con un **webhook** (`/api/stripe/webhook`, firma verificata): solo allora l'ordine diventa `pagato`, scala la giacenza e compare in Ordini/Spedizioni.
3. La chiave segreta Stripe resta **solo nel gestionale**. Il sito non la vede mai.

## Regole di sicurezza
- Il sito è pubblico: nessuna password o chiave dentro `index.html`.
- CORS: il gestionale accetta richieste solo dal dominio del sito (GitHub Pages, poi SiteGround).
- Prezzi, totali, giacenze e stati ordine li decide sempre il gestionale.

## Già pronto
`gestionale-demo/sito_api.py` è un server di prova che rispetta questo contratto (dati di esempio). Serve per provare il collegamento sul Mac prima di avere il gestionale vero: il gestionale vero dovrà solo rispondere agli stessi indirizzi.

## Ancora da costruire
Pagina di cassa del sito (dati cliente + invio ordine + pagamento), webhook Stripe, area Account clienti, caricamento foto dal gestionale.
