# Collegamento sito ⇄ gestionale OVERSOUND

Il sito legge tutto dal gestionale (https://oversound.pythonanywhere.com) e gli invia gli ordini.
Serve il **gestionale aggiornamento 33** o successivo (tempi di spedizione, usato, account, varianti, categorie con immagine, filtri).

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
| Tempi di spedizione e prodotti ordinabili anche a giacenza 0 | Sito web > Tempi di spedizione |
| Account dei clienti (attivi o no, password provvisorie) | Sito web > Account clienti |
| Prezzo del sito diverso dal negozio | Scheda prodotto o Catalogo online |
| Nuovo / Usato garantito / Usato / Ricondizionato / Ex demo | Scheda prodotto > Condizione |
| Varianti (es. stesso modello in colori diversi) | Scheda prodotto > Varianti |
| Simbolo o immagine e ordine di categorie e sottocategorie | Categorie e marche |
| Iscritti newsletter e avvisi | Sito web > Iscritti e avvisi |

**Importante:** in Sito web > Impostazioni sito, «Indirizzo del sito» deve essere solo `https://oversound08.github.io`
(senza /Oversound). Quando il sito andrà su oversound.it, cambialo in `https://oversound.it`.
Se non coincide il sito non riesce a leggere i dati e mostra i dati di esempio.

## Indirizzi usati dal sito
Lettura: `/api/lista`, `/api/prodotto/<slug>`, `/api/config`, `/api/vetrina`, `/api/recensioni`, `/api/categorie`.
Account: `/api/account/registra`, `accedi`, `recupera`, `io`, `aggiorna`, `password`, `esci` (token salvato solo nel browser del cliente).
Pagamenti online: `/api/pagamento/<ordine>`, `/api/pagamento/ritorno`, `/api/pagamento/annulla`.
Invio: `/api/ordini` (prezzi e totale li ricalcola sempre il gestionale), `/api/recensioni`, `/api/newsletter`, `/api/avvisi`.

## Regole
- «Usato»: lo decide la Condizione nella scheda prodotto (Usato garantito, Usato, Ricondizionato, Ex demo). Con un gestionale vecchio vale ancora la parola «usato» nella categoria.
- Prezzi sempre con i centesimi (es. 1.299,90 €). Gli ordini del sito sono salvati IVA inclusa: il totale è esattamente quello mostrato.
- Disponibilità: «Disponibile», «Su ordinazione · 9/16 giorni» (giacenza 0 ma ordinabile, secondo i Tempi di spedizione) o «Esaurito».
- Le sottocategorie sono riquadri di navigazione in cima al catalogo; i filtri (prezzo, condizione, disponibilità, tempi, marca e caratteristiche tecniche) sono a parte.
- I metodi di pagamento mostrati nella cassa sono quelli accesi in Sito web > Pagamenti. Con carta o PayPal il cliente va sulla pagina di pagamento e torna al sito; l'ordine passa da solo a «Da spedire».
- Nel sito non ci sono password o chiavi: il repository è pubblico.
