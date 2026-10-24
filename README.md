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
Contratto completo in `API-GESTIONALE.md`.
- **Prova sul Mac:** `cd gestionale-demo && pip3 install flask && python3 sito_api.py`; poi, nella cartella del sito, `python3 -m http.server 8000` e apri `http://127.0.0.1:8000/index.html?api=http://127.0.0.1:5000`.
- **Online:** quando il gestionale ha le API del contratto, in `index.html` scrivi `const API_URL='https://oversound.pythonanywhere.com'`. Finché è `null` il sito usa i dati di esempio. Il gestionale deve consentire l'accesso dal dominio del sito (CORS).

## Andare online su SiteGround
1. Carica `index.html` nella cartella `public_html` (Site Tools → File Manager, oppure FTP).
2. Collega il dominio e attiva HTTPS (SSL gratuito di SiteGround).
3. In `index.html`: togli la riga `<meta name="robots" content="noindex">` (altrimenti Google non lo trova) e imposta `const DEMO_MODE=false`.

## Prima del lancio
Dati reali dell'azienda (numero WhatsApp, indirizzo, P.IVA, orari: sezione `AZIENDA`), foto dei prodotti, testi di spedizioni/resi/privacy,
pagamenti collegati al gestionale, banner cookie se aggiungi statistiche o pubblicità.
