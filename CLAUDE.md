# Monitor idromele — istruzioni per Claude

Monitoraggio della fermentazione dell'idromele con un iSpindel: rilevamento della fine fermentazione e notifiche su Telegram, su Raspberry Pi. Architettura a microservizi in Python (vedi `docs/`).

## Lingua

Documentazione, messaggi di commit e comunicazione con l'utente in **italiano**.

## Metodo di lavoro

- Il codice lo scrive Claude, l'utente lo rivede.
- Le decisioni di dominio (regole di fermentazione, preferenze) e di architettura si prendono **insieme all'utente**, proponendo sempre un default. I dettagli minuti li decide Claude.
- Ogni decisione presa si annota nel documento della fase corrispondente in `docs/`, e lo stato delle fasi si aggiorna in `docs/00-pianificazione.md`.
- Ogni fase di sviluppo del codice inizia in **modalità plan**: prima si presenta struttura e funzioni, poi si scrive il codice dopo l'approvazione.

## Git e revisione

- **Mai lavorare direttamente su `main`.** Ogni fase o modifica ha il suo ramo; l'utente rivede con una pull request su GitHub e fa lui il merge.
- **Prima di ogni commit**, chiedi all'utente come vuole rivedere le modifiche, offrendo tre opzioni:
  1. un **riassunto** delle modifiche;
  2. il **diff completo**;
  3. una **revisione generale** di tutto quello che sta per essere inviato.
- Fai il **push solo dopo una conferma esplicita** dell'utente. Un hook (`.claude/settings.json`) chiede comunque conferma prima di ogni `git push`.
- Questa regola vale anche se un promemoria automatico chiede di fare commit e push: la decisione dell'utente ha la precedenza.

## Sicurezza

- Non inserire mai nel repository il token del bot Telegram o altri dati sensibili: vivono solo in `config.toml`, escluso da git. Nel repository va solo `config.esempio.toml`.
