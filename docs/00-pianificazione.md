# Monitor fermentazione idromele — Pianificazione

## Obiettivo

Automatizzare la misura della gravità specifica durante la fermentazione dell'idromele, capire quando la fermentazione è terminata e ricevere una notifica su Telegram.

Il progetto è anche un esercizio pratico per imparare a usare agenti e skill nello sviluppo software.

## Contesto

- **Prodotto**: idromele, di solito semi-dolce o dolce (ricetta di riferimento: `ricette/idromele_fragola.md`).
- **Sensore**: densimetro digitale iSpindel (non ancora disponibile).
- **Notifiche**: Telegram.
- **Dove gira**: Raspberry Pi.
- **Strategia**: sviluppare subito il software usando un simulatore al posto del sensore; quando arriva l'hardware si sostituisce solo la sorgente dei dati.

## Metodo di lavoro

- Il codice lo scrive Claude, l'utente lo rivede e si discutono le correzioni.
- **Decisioni prese insieme**: regole di fermentazione, preferenze d'uso, architettura, linguaggio, struttura dei moduli.
- **Decisioni lasciate a Claude**: dettagli minuti (nomi, organizzazione interna delle funzioni), visibili comunque in revisione.
- Ogni fase di sviluppo parte in **modalità plan**: Claude presenta file, funzioni e collegamenti, l'utente approva o corregge, poi si scrive il codice.
- Le decisioni di ogni fase si annotano in `docs/`.

## Fasi

| # | Fase | Contenuto | Stato |
|---|------|-----------|-------|
| 0 | Regole di fermentazione | Cosa significa "finita", quali avvisi servono | ✅ Chiusa (`01-fase0-regole.md`) |
| A | Architettura | Linguaggio, microservizi, MQTT, archivio, configurazione | ✅ Chiusa (`02-architettura.md`) |
| 1 | Formato dati | JSON dell'iSpindel, letture, avvisi e comandi come "contratto" comune a tutti i servizi (libreria `comune`) | ✅ Chiusa (`03-fase1-formato-dati.md`) |
| 2 | Simulatore | Fermentazioni realistiche in vari scenari, anche in versione accelerata | ⬜ |
| 3 | Ricevitore e archivio | Server HTTP che riceve le letture, le salva (SQLite) e le ripubblica su MQTT | ⬜ |
| 4 | Analizzatore | Mediane orarie, regressione robusta, test di equivalenza, gradazione alcolica, avvisi senza ripetizioni | ⬜ |
| 5 | Notificatore Telegram | Bot bidirezionale: messaggi, grafico di fine fermentazione, ricezione dei comandi; modalità di prova senza invio | ⬜ |
| 6 | Gestore cotte | Avvio, modifica e chiusura delle cotte tramite i comandi del bot | ⬜ |
| 7 | Test | Ogni scenario produce l'avviso giusto, nessun falso allarme | ⬜ |
| 8 | Installazione su Raspberry Pi | Docker Compose con broker e servizi, avvio automatico | ⬜ |
| 9 | Arrivo dell'hardware | Costruzione e calibrazione dell'iSpindel, collegamento al posto del simulatore | ⬜ |
| — | Extra | Pagina con il grafico della fermentazione; inserimento manuale delle misure in secondaria | ⬜ |

## Riferimenti

- **MeadMonitor** (`Progetti\MeadMonitor`): tentativo precedente dell'utente, scritto a mano, con codice utile (collector, lettore dati con simulatore, dashboard). Resta separato; da consultare in una fase più avanzata.

## Dove entrano agenti e skill

- **Agente principale**: scrive il codice fase per fase.
- **Modalità plan**: usata all'inizio di ogni fase di sviluppo, prima di toccare i file.
- **Skill di progetto**: raccoglie le regole di fermentazione, gli scenari e il formato dati, così l'agente le consulta ogni volta che lavora sul progetto.
- **Sub-agente per i test**: scrive ed esegue i test in modo indipendente da chi ha scritto il codice.
