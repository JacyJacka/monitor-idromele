# Architettura

Stato: ✅ chiusa

## Decisioni principali

| Tema | Decisione |
|------|-----------|
| Linguaggio | Python |
| Struttura | Microservizi: un servizio per responsabilità, ognuno nella sua cartella con le sue dipendenze |
| Repository | Unico repository (monorepo) con una cartella per servizio |
| Comunicazione | MQTT tramite broker (Mosquitto) |
| Archivio | Database SQLite posseduto dal ricevitore; l'analizzatore lo legge soltanto |
| Contratto comune | Libreria condivisa `comune` con i formati di letture e avvisi |
| Esecuzione su Raspberry Pi | Docker Compose: un container per servizio, broker incluso |
| Configurazione | File TOML locale escluso da git; nel repository solo un file di esempio |

## Flusso dei dati

```
simulatore / iSpindel ──MQTT──► broker ──MQTT──► ricevitore ──► database
                                                                  │
                                                         (legge ogni 15 min)
                                                                  ▼
            Telegram ◄── notificatore ◄──MQTT── broker ◄──MQTT── analizzatore
```

Nessun servizio parla direttamente con un altro: tutti pubblicano sul broker o leggono dal broker. Il simulatore e l'iSpindel vero sono intercambiabili perché pubblicano lo stesso formato sugli stessi argomenti.

## Servizi

### simulatore
- Imita l'iSpindel e pubblica letture sul broker, nello stesso formato del sensore vero.
- Genera fermentazioni realistiche in vari scenari (normale, lenta, bloccata, rumorosa, sensore che smette di trasmettere), anche in versione accelerata.
- Verrà spento quando arriva l'hardware.

### ricevitore
- È iscritto agli argomenti dell'iSpindel sul broker.
- Valida le letture e le salva nel database, associandole alla cotta in corso.
- È l'unico servizio che scrive le letture nel database.

### analizzatore
- Ogni **15 minuti** legge dal database le letture della cotta in corso.
- Applica le regole della fase 0 e decide quali avvisi scattano.
- Pubblica gli avvisi sul broker.
- Il controllo è periodico, e non solo all'arrivo di una lettura, perché diversi avvisi scattano proprio in assenza di novità (sensore muto, fermentazione non partita, promemoria frutta).

### notificatore
- È iscritto all'argomento degli avvisi sul broker.
- Formatta i messaggi e li invia su Telegram.
- Ha una modalità di prova che stampa i messaggi invece di inviarli.

### dashboard (più avanti)
- Pagina con il grafico della fermentazione.

## Gestione degli avvisi

- L'analizzatore **ricorda gli avvisi già inviati** per la cotta in corso, in una tabella sua, così il ricordo sopravvive ai riavvii.
- Gli avvisi "una tantum" (partita, finita, promemoria frutta) si inviano **una sola volta** per cotta.
- Gli avvisi che possono ripetersi (temperatura alta, sensore muto, batteria) rispettano un **intervallo minimo** tra un messaggio e l'altro (proposta: 6 ore) finché il problema persiste.

## Argomenti MQTT (proposta)

| Argomento | Chi pubblica | Chi legge | Contenuto |
|-----------|--------------|-----------|-----------|
| `ispindel/<nome>/<campo>` | iSpindel / simulatore | ricevitore | Un valore per argomento (gravità, temperatura, batteria…) |
| `idromele/avvisi` | analizzatore | notificatore | Un avviso in formato JSON |

Il formato esatto dei messaggi dell'iSpindel si definisce nella fase 1.

## Struttura del repository (proposta)

```
monitor-idromele/
├── comune/              ← libreria condivisa: formati di letture e avvisi
├── servizi/
│   ├── simulatore/
│   ├── ricevitore/
│   ├── analizzatore/
│   └── notificatore/
├── docker-compose.yml   ← avvia broker e servizi
├── config.esempio.toml  ← configurazione di esempio, senza dati sensibili
├── docs/
└── ricette/
```

## Note tecniche

- Il database SQLite è condiviso tra i container tramite un volume Docker; si usa la modalità WAL, così l'analizzatore può leggere mentre il ricevitore scrive.
- Il token del bot Telegram vive solo nel file di configurazione locale (`config.toml`), escluso da git.

## Da definire nelle fasi successive

- **Formato dei messaggi** dell'iSpindel e degli avvisi (fase 1).
- **Gestione delle cotte**: come si avvia una nuova cotta con i suoi parametri (nome, OG, FG attesa) e quale servizio se ne occupa.
- **Versione di Python** e strumenti di gestione delle dipendenze.
