# Fase 1 — Formato dei dati

Stato: 🟡 in corso

Questi formati sono il "contratto" comune a tutti i servizi. Vengono definiti una sola volta nella libreria `comune`.

## 1. Messaggio dell'iSpindel (HTTP)

L'iSpindel, in modalità HTTP, invia a ogni risveglio una richiesta `POST` con un unico JSON che contiene tutti i valori della stessa misura:

```json
{
  "name": "fermentatore1",
  "ID": "2E6753",
  "token": "",
  "interval": 900,
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

Il ricevitore trasforma il messaggio dell'iSpindel in una **lettura**, che è il formato usato nel database e pubblicato su `idromele/letture`.

| Campo | Esempio | Note |
|-------|---------|------|
| `sensore` | `fermentatore1` | nome dell'iSpindel (`name`) |
| `istante` | `2026-11-05T00:10:00+01:00` | assegnato dal ricevitore all'arrivo: l'iSpindel non ha un orologio |
| `gravita` | `1.0452` | gravità specifica (SG), non gradi Plato |
| `angolo` | `52.34` | inclinazione grezza in gradi, salvata sempre per poter ricalcolare la gravità dopo una nuova calibrazione |
| `temperatura` | `20.5` | in °C |
| `batteria` | `3.92` | in volt |
| `rssi` | `-67` | qualità del segnale Wi-Fi in dBm |
| `intervallo` | `900` | intervallo di invio in secondi, utile per tarare l'avviso di sensore muto |

### Validazione (proposta)

Una lettura con valori fuori da questi intervalli viene salvata ma marcata come **non valida**, e l'analisi la ignora:

| Campo | Intervallo accettato |
|-------|----------------------|
| `gravita` | 0,980 – 1,200 |
| `angolo` | 0 – 90° |
| `temperatura` | -5 – 50 °C |
| `batteria` | 2,5 – 4,5 V |

## 3. Avviso

L'analizzatore pubblica su `idromele/avvisi` un JSON con i soli **dati**; il testo in italiano lo compone il notificatore.

```json
{
  "tipo": "fermentazione_finita",
  "cotta": "fragola-2027",
  "istante": "2027-07-20T09:15:00+02:00",
  "livello": "info",
  "dati": {
    "gravita": 1.0021,
    "fg_attesa": 1.004,
    "giorni_dall_inizio": 24
  }
}
```

### Tipi di avviso

| `tipo` | `livello` |
|--------|-----------|
| `fermentazione_partita` | info |
| `fermentazione_non_partita` | attenzione |
| `fermentazione_vigorosa` | attenzione |
| `promemoria_frutta` | info |
| `fermentazione_finita` | info |
| `temperatura_alta` | attenzione |
| `sensore_muto` | attenzione |
| `batteria_scarica` | attenzione |

Gli avvisi si pubblicano con **QoS 1** ("almeno una volta"), così non vanno persi.

## Decisioni ancora aperte

- **Intervallo di invio**: 15 minuti (più dati, batteria circa un mese e mezzo) o 30 minuti (batteria quasi tre mesi).
- **Soglia batteria**: provvisoria a **3,5 V** (batteria al litio 18650), da confermare quando si costruisce il sensore.
