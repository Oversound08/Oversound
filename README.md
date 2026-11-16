# OVERSOUND – Sito e-commerce

Sito statico (un solo file `index.html`): React, nessuna installazione, nessuna compilazione.
Funziona così com'è su GitHub Pages e su SiteGround.

## Pubblicare su GitHub (gratis, senza comandi)
1. Su github.com: **New repository** → nome `oversound` → **Public** → Create.
2. **Add file → Upload files**: carica `index.html`, `.nojekyll` e `README.md` → Commit.
3. **Settings → Pages**: Source = *Deploy from a branch*, Branch = `main`, cartella `/ (root)` → Save.
4. Dopo 1-2 minuti il sito è su `https://TUO-NOME-UTENTE.github.io/oversound/`.

> Con il piano gratuito il repository deve essere pubblico: non metterci mai password o chiavi (password, chiavi dei pagamenti restano solo nel gestionale).

## Collegare il gestionale
Il sito è già collegato a `https://oversound.pythonanywhere.com` (riga `API_URL` in `index.html`). Serve il gestionale aggiornamento 26 e, nelle sue Impostazioni sito, l'indirizzo `https://oversound08.github.io`. Dettagli in `COLLEGAMENTO-GESTIONALE.md`. Con `API_URL=null` il sito usa solo dati di esempio.

## Andare online su SiteGround
1. Carica `index.html` nella cartella `public_html` (Site Tools → File Manager, oppure FTP).
2. Collega il dominio e attiva HTTPS (SSL gratuito di SiteGround).
3. In `index.html`: togli la riga `<meta name="robots" content="noindex">` (altrimenti Google non lo trova) e imposta `const DEMO_MODE=false`.

## Indirizzi delle pagine
Il sito usa indirizzi normali: `oversound.it/carrello/`, `oversound.it/prodotto/nome-prodotto/`, `oversound.it/categoria/chitarre-e-bassi/`.
I vecchi indirizzi con `#` (es. `oversound.it/#/carrello`) funzionano ancora: il sito li trasforma da solo.
Le pagine fisse (catalogo, carrello, servizi, informative), `404.html` e `sitemap.xml` le crea `strumenti/genera_pagine.py`, che GitHub avvia da solo.
Su GitHub Pages `404.html` fa aprire il sito anche agli indirizzi che non hanno una pagina (es. `/ordine/…`).
Su SiteGround (Apache) serve in più un file `.htaccess` con `ErrorDocument 404 /404.html`.

## Conversioni per la pubblicità
Quando un ordine viene completato o un cliente tocca WhatsApp, telefono o email, il sito avvisa Google Ads/Analytics e Meta,
ma solo se i loro codici sono installati (pacchetto A). L'etichetta della conversione «Acquisto» di Google Ads va in `ADS_CONVERSIONE` in `index.html`.

## Prima del lancio
Dati reali dell'azienda (numero WhatsApp, indirizzo, P.IVA, orari: sezione `AZIENDA`), foto dei prodotti, testi di spedizioni/resi/privacy,
pagamento con carta, banner cookie se aggiungi statistiche o pubblicità.

