# Collegamento sito ⇄ gestionale OVERSOUND

Il sito legge tutto dal gestionale (https://oversound.pythonanywhere.com) e gli invia gli ordini.
Serve il **gestionale aggiornamento 24** o successivo.

## Cosa si gestisce dal gestionale
| Cosa | Dove |
|---|---|
| Prodotti, prezzi, giacenze, foto, descrizioni | Prodotti (solo quelli pubblicati sul sito) |
| Prodotti in evidenza e prezzo precedente (offerte) | Sito web > In evidenza e offerte |
| Slide della home (foto/video, testo, link) | Sito web > Slide |
| Orari, WhatsApp, social, giorni di consegna | Sito web > Contenuti |
| Dati azienda (indirizzo, P.IVA, email) | Impostazioni |
| Spese di spedizione, coupon | Sito web > Impostazioni sito e Coupon |
| Metodi di pagamento (bonifico, contrassegno, carta/Apple Pay/Google Pay con Stripe, PayPal, altri) | Sito web > Pagamenti |
| Recensioni | Sito web > Recensioni (si approvano prima di comparire) |
| Ordini del sito | Ordini sito e Amazon |
| Iscritti newsletter e avvisi | Sito web > Iscritti e avvisi |

**Importante:** in Sito web > Impostazioni sito, «Indirizzo del sito» deve essere solo `https://oversound08.github.io`
(senza /Oversound). Quando il sito andrà su oversound.it, cambialo in `https://oversound.it`.
Se non coincide il sito non riesce a leggere i dati e mostra i dati di esempio.

## Indirizzi usati dal sito
Lettura: `/api/lista`, `/api/prodotto/<slug>`, `/api/config`, `/api/vetrina`, `/api/recensioni`.
Pagamenti online: `/api/pagamento/<ordine>`, `/api/pagamento/ritorno`, `/api/pagamento/annulla`.
Invio: `/api/ordini` (prezzi e totale li ricalcola sempre il gestionale), `/api/recensioni`, `/api/newsletter`, `/api/avvisi`.

## Regole
- «Usato»: un prodotto è mostrato come usato se la sua categoria o sottocategoria contiene la parola «usato».
- I metodi di pagamento mostrati nella cassa sono quelli accesi in Sito web > Pagamenti. Con carta o PayPal il cliente va sulla pagina di pagamento e torna al sito; l'ordine passa da solo a «Da spedire».
- Nel sito non ci sono password o chiavi: il repository è pubblico.
