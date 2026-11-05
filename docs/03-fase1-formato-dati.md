# Fase 1 — Formato dei dati

Stato: ✅ chiusa

Questi formati sono il "contratto" comune a tutti i servizi. Vengono definiti una sola volta nella libreria `comune`.

## 1. Messaggio dell'iSpindel (HTTP)

L'iSpindel, in modalità HTTP, invia a ogni risveglio una richiesta `POST` con un unico JSON che contiene tutti i valori della stessa misura:

```json
{
  "name": "fermentatore1",
  "ID": "2E6753",
  "token": "",
  "interval": 1800,
  "temperature": 20.5,
  "temp_units": "C",
  "gravity": 1.0452,
  "angle": 52.34,
  "battery": 3.92,
  "RSSI": -67
}
```

Il simulatore invia lo stesso identico formato, allo stesso indirizzo.

**Da verificare con il sensore reale**: maiuscole/minuscole dei nomi dei campi (es. `RSSI` / `rssi`) e la presenza di campi aggiuntivi a seconda del firmware. Il ricevitore accetterà entrambe le grafie e ignorerà i campi sconosciuti.

**Proposta di indirizzo**: `POST http://<raspberry>:8080/ispindel`

## 2. Lettura (formato interno)

Il ricevitore trasforma il messaggio dell'iSpindel in una **lettura**, che è il formato usato nel database. Dopo il salvataggio, il ricevitore **ripubblica la lettura** in JSON su `idromele/letture`, così altri servizi (come la futura dashboard) possono riceverla in diretta senza interrogare il database.

| Campo | Esempio | Note |
|-------|---------|------|
| `sensore` | `fermentatore1` | nome dell'iSpindel (`name`) |
| `istante` | `2026-11-05T00:10:00+01:00` | assegnato dal ricevitore all'arrivo: l'iSpindel non ha un orologio |
| `gravita` | `1.0452` | gravità specifica (SG), non gradi Plato |
| `angolo` | `52.34` | inclinazione grezza in gradi, salvata sempre per poter ricalcolare la gravità dopo una nuova calibrazione |
| `temperatura` | `20.5` | in °C |
| `batteria` | `3.92` | in volt |
| `rssi` | `-67` | qualità del segnale Wi-Fi in dBm |
| `intervallo` | `1800` | intervallo di invio in secondi, utile per tarare l'avviso di sensore muto |

### Validazione

Una lettura con valori fuori dagli intervalli accettati viene salvata ma marcata come **non valida**, e l'analisi la ignora. Le letture non valide restano nel database, così si possono studiare in seguito.

Tutti gli intervalli sono **configurabili** nel file di configurazione; questi sono i valori predefiniti:

| Campo | Intervallo predefinito |
|-------|------------------------|
| `gravita` | 0,980 – 1,200 |
| `angolo` | 0 – 90° |
| `temperatura` | -5 – 50 °C |
| `batteria` | 2,5 – 4,5 V |

## 3. Avviso

L'analizzatore pubblica su `idromele/avvisi` un JSON con i soli **dati**; il testo in italiano lo compone il notificatore. Così l'analizzatore si occupa solo di *cosa* succede e il notificatore solo di *come* comunicarlo: cambiare lo stile dei messaggi o aggiungere un canale non tocca la logica di analisi.

```json
{
  "tipo": "fermentazione_finita",
  "cotta": "fragola-2027",
  "istante": "2027-07-20T09:15:00+02:00",
  "livello": "info",
  "dati": {
    "gravita": 1.0021,
    "fg_attesa": 1.004,
    "giorni_dall_inizio": 24,
    "og": 1.100,
    "fonte_og": "manuale",
    "abv": 13.9,
    "serie": [["2027-06-26T10:00:00+02:00", 1.0998], ["..."]],
    "regressione": {
      "inizio": "2027-07-13T09:00:00+02:00",
      "pendenza_7g": 0.0002,
      "intervallo_confidenza_7g": [-0.0004, 0.0008],
      "intercetta": 1.0023
    }
  }
}
```

### Dati aggiuntivi a fine fermentazione

- **Gradazione alcolica** (`abv`): calcolata dall'analizzatore con la formula per mosti ad alta densità, configurabile:

  ABV = 76,08 × (OG − FG) / (1,775 − OG) × FG / 0,794

  La formula standard da birra, ABV ≈ (OG − FG) × 131,25, resta disponibile come alternativa, ma con le OG tipiche dell'idromele tende a sottostimare.
- **Fonte dell'OG** (`fonte_og`): `manuale` se inserita dall'utente all'avvio della cotta (fonte principale), `sensore` se ricavata dalle prime letture prima del calo (riserva). Il messaggio indica quale è stata usata.
- **Nota**: con la frutta in primaria, le fragole continuano a cedere zucchero per giorni, quindi l'OG misurata all'inizio è un po' più bassa di quella reale e la gradazione risulta leggermente sottostimata. Nessuna correzione automatica.
- **Grafico**: l'avviso include la serie delle mediane orarie di tutta la cotta (`serie`) e i parametri della retta dell'ultima settimana (`regressione`). Il notificatore disegna il grafico (curva della gravità, retta di regressione evidenziata, linea tratteggiata della FG attesa se presente) e lo invia su Telegram con il messaggio. Se il disegno fallisce, invia comunque il messaggio di testo.

### Tipi di avviso

| `tipo` | `livello` |
|--------|-----------|
| `cotta_non_registrata` | attenzione |
| `fermentazione_partita` | info |
| `fermentazione_non_partita` | attenzione |
| `fermentazione_vigorosa` | attenzione |
| `promemoria_frutta` | info |
| `fermentazione_finita` | info |
| `temperatura_alta` | attenzione |
| `sensore_muto` | attenzione |
| `batteria_scarica` | attenzione |

`cotta_non_registrata` scatta quando arrivano letture ma nessuna cotta è attiva, tipicamente subito dopo aver messo l'iSpindel nel mosto. Si ripete ogni **6 ore**, **solo di giorno** (predefinito: dalle 8:00 alle 22:00), finché la cotta non viene registrata: un promemoria che cadrebbe di notte viene rimandato alle 8:00. Intervallo e fascia oraria sono configurabili. Il **primo** avviso invece parte subito, a qualsiasi ora: arriva quando l'utente ha appena messo il sensore nel mosto, quindi è sveglio e accanto al fermentatore. Le letture nel frattempo vengono salvate e, alla registrazione, risultano associate alla nuova cotta in base al periodo.

### Conferme del gestore cotte

Il gestore cotte usa lo stesso argomento e lo stesso formato per rispondere ai comandi:

| `tipo` | `livello` |
|--------|-----------|
| `cotta_avviata` | info |
| `cotta_modificata` | info |
| `cotta_chiusa` | info |
| `stato_cotta` | info |
| `comando_non_valido` | attenzione |

Gli avvisi si pubblicano con **QoS 1** ("almeno una volta"), così non vanno persi.

## 4. Comando

Il notificatore riceve i messaggi dell'utente dal bot e li ripubblica su `idromele/comandi`, senza interpretarli. Il gestore cotte li interpreta.

```json
{
  "testo": "/nuovacotta fragola-2027 og=1.100 fg=1.004",
  "istante": "2027-06-26T10:05:00+02:00",
  "origine": "telegram"
}
```

Comandi previsti (proposta, da dettagliare nella fase del gestore cotte):

| Comando | Effetto |
|---------|---------|
| `/nuovacotta <nome> og=<valore> fg=<valore>` | Avvia una cotta; `og` e `fg` facoltativi |
| `/modifica og=<valore>` | Corregge i dati della cotta attiva |
| `/fine` | Chiude la cotta attiva, ad esempio dopo il travaso |
| `/stato` | Gravità attuale, giorni trascorsi, ultima lettura |

Il notificatore accetta comandi **solo dalla chat Telegram autorizzata**, indicata in `config.toml`: chiunque trovasse il bot non potrebbe gestire le cotte.

## Parametri del sensore

- **Intervallo di invio**: **30 minuti** (`interval: 1800`). Batteria stimata quasi tre mesi; due letture all'ora bastano per le mediane orarie dell'analizzatore.
- **Soglia batteria**: **3,5 V** (batteria al litio 18650), provvisoria, da confermare quando si costruisce il sensore.
- **Unità della gravità**: il sensore va configurato in **gravità specifica (SG)**, non in gradi Plato.
