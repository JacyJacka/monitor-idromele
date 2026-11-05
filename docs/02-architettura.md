# Architettura

Stato: ✅ chiusa

## Decisioni principali

| Tema | Decisione |
|------|-----------|
| Linguaggio | Python |
| Struttura | Microservizi: un servizio per responsabilità, ognuno nella sua cartella con le sue dipendenze |
| Repository | Unico repository (monorepo) con una cartella per servizio |
| Comunicazione | Ibrida: HTTP con JSON tra sensore e ricevitore, MQTT tramite broker (Mosquitto) tra i servizi |
| Archivio | Database SQLite condiviso, in cui ogni servizio scrive solo le sue tabelle: letture (ricevitore), cotte (gestore cotte), avvisi inviati (analizzatore) |
| Contratto comune | Libreria condivisa `comune` con i formati di letture, avvisi e comandi |
| Esecuzione su Raspberry Pi | Docker Compose: un container per servizio, broker incluso |
| Configurazione | File TOML locale escluso da git; nel repository solo un file di esempio |

## Flusso dei dati

```
simulatore / iSpindel ──HTTP (JSON)──► ricevitore ──► database ◄── gestore cotte
                                           │                │             ▲   │
                                           │       (legge ogni 15 min)    │   │ idromele/avvisi
                                     MQTT  │                ▼             │   │ (conferme)
                          idromele/letture ▼           analizzatore       │   │
                                        broker ◄──MQTT──────┘             │   │
                                         │  ▲  idromele/avvisi            │   │
                                    MQTT ▼  └───────── idromele/comandi ──┘   │
                Telegram ◄────────► notificatore ◄────────────────────────────┘
```

Telegram è l'unico punto di contatto con l'utente, in entrambe le direzioni: riceve gli avvisi e accetta i comandi per gestire le cotte.

Il sensore invia ogni lettura al ricevitore con una richiesta HTTP, in un unico messaggio JSON con tutti i valori. Il simulatore fa esattamente lo stesso, quindi i due sono intercambiabili.

Tra i servizi, invece, nessuno parla direttamente con un altro: tutti pubblicano sul broker o leggono dal broker.

**Piano B**: se l'HTTP dovesse dare problemi con il sensore reale, si passa a MQTT anche per il sensore, con i valori pubblicati su argomenti separati (`ispindel/<nome>/<campo>`) e ricomposti dal ricevitore in un'unica lettura.

## Servizi

### simulatore
- Imita l'iSpindel e invia letture al ricevitore via HTTP, nello stesso formato JSON del sensore vero.
- Genera fermentazioni realistiche in vari scenari (normale, lenta, bloccata, rumorosa, sensore che smette di trasmettere), anche in versione accelerata.
- Verrà spento quando arriva l'hardware.

### ricevitore
- È un piccolo server web che accoglie le richieste HTTP dell'iSpindel.
- Valida le letture e le salva nel database, con sensore e istante.
- È l'unico servizio che scrive le letture nel database.
- Non conosce le cotte: l'associazione tra letture e cotta si fa in base al periodo in cui la cotta era attiva.
- Dopo il salvataggio, ripubblica la lettura su `idromele/letture`, così altri servizi (come la futura dashboard) possono riceverla in diretta.

### analizzatore
- Ogni **15 minuti** legge dal database le letture della cotta in corso.
- Applica le regole della fase 0 e decide quali avvisi scattano.
- Pubblica gli avvisi sul broker.
- Il controllo è periodico, e non solo all'arrivo di una lettura, perché diversi avvisi scattano proprio in assenza di novità (sensore muto, fermentazione non partita, promemoria frutta).
- Se arrivano letture ma **nessuna cotta è attiva**, pubblica l'avviso `cotta_non_registrata`, ripetuto finché la cotta non viene registrata.
- A fine fermentazione calcola la gradazione alcolica e include nei dati dell'avviso la serie delle mediane orarie e la retta di regressione, per il grafico.

### notificatore
- È l'**unico servizio che parla con Telegram**: un bot può ricevere i messaggi in un solo programma alla volta.
- È iscritto a `idromele/avvisi`: formatta i messaggi e li invia; a fine fermentazione disegna il grafico (matplotlib) e lo invia con il messaggio, ripiegando sul solo testo se il disegno fallisce.
- Riceve i comandi dell'utente dal bot e li ripubblica su `idromele/comandi`, senza interpretarli.
- Accetta comandi **solo dalla chat autorizzata**, configurata in `config.toml`.
- Ha una modalità di prova che stampa i messaggi invece di inviarli.

### gestore cotte
- È iscritto a `idromele/comandi` e gestisce l'avvio, la modifica e la chiusura delle cotte (nome, OG, FG attesa, sensore).
- È l'unico servizio che scrive i dati delle cotte nel database, nella sua tabella.
- Risponde ai comandi pubblicando conferme ed errori su `idromele/avvisi`, così arrivano all'utente tramite il notificatore.
- In futuro la dashboard potrà gestire le cotte pubblicando gli stessi comandi.

### dashboard (più avanti)
- Pagina con il grafico della fermentazione.
- Punto ideale per inserire e modificare i dati delle cotte, pubblicando gli stessi comandi del bot.

## Gestione degli avvisi

- L'analizzatore **ricorda gli avvisi già inviati** per la cotta in corso, in una tabella sua, così il ricordo sopravvive ai riavvii.
- Gli avvisi "una tantum" (partita, finita, promemoria frutta) si inviano **una sola volta** per cotta.
- Gli avvisi che possono ripetersi (temperatura alta, sensore muto, batteria) rispettano un **intervallo minimo** tra un messaggio e l'altro (proposta: 6 ore) finché il problema persiste.

## Argomenti MQTT (proposta)

| Argomento | Chi pubblica | Chi legge | Contenuto |
|-----------|--------------|-----------|-----------|
| `idromele/letture` | ricevitore | dashboard (futura), chiunque interessato | Una lettura salvata, in formato JSON |
| `idromele/avvisi` | analizzatore, gestore cotte | notificatore | Un avviso o una conferma in formato JSON |
| `idromele/comandi` | notificatore (in futuro anche dashboard) | gestore cotte | Un comando dell'utente in formato JSON |

I formati dei messaggi sono definiti in `03-fase1-formato-dati.md`.

## Struttura del repository (proposta)

```
monitor-idromele/
├── comune/              ← libreria condivisa: formati di letture e avvisi
├── servizi/
│   ├── simulatore/
│   ├── ricevitore/
│   ├── analizzatore/
│   ├── notificatore/
│   └── gestore_cotte/
├── docker-compose.yml   ← avvia broker e servizi
├── config.esempio.toml  ← configurazione di esempio, senza dati sensibili
├── docs/
└── ricette/
```

## Note tecniche

- Il database SQLite è condiviso tra i container tramite un volume Docker; si usa la modalità WAL, così i servizi possono leggere mentre un altro scrive. Ogni servizio scrive solo nelle proprie tabelle.
- Il token del bot Telegram vive solo nel file di configurazione locale (`config.toml`), escluso da git.

## Da definire nelle fasi successive

- **Versione di Python** e strumenti di gestione delle dipendenze.
