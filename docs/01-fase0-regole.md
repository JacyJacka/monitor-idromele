# Fase 0 — Regole di fermentazione

Stato: ✅ chiusa

## Contesto d'uso

- **Primaria** in un unico fermentatore cilindrico da 10-15 litri (vetro o plastica alimentare, **non acciaio**: blocca il Wi-Fi dell'iSpindel).
- Frutta in una **rete con pesi** sul fondo: l'iSpindel galleggia libero.
- **Rimescolamento quotidiano**: produce disturbi momentanei nelle letture, che il software deve filtrare.
- L'iSpindel è usato **solo in primaria**. La secondaria avviene in due damigiane da 5 litri a collo stretto, dove il sensore non entra: lì le misure restano manuali.
- **Nutrienti**: tutti all'inizio, in un'unica dose. Nessun promemoria necessario.
- **Temperatura**: ambiente di casa, 19-21°C d'inverno; d'estate segue la temperatura stagionale.

## Valori di riferimento (ricetta idromele alla fragola)

| Parametro | Valore |
|-----------|--------|
| OG stimata | ~1,100 |
| FG attesa | 0,998-1,005 |
| Durata primaria tipica | 2-4 settimane |
| Contatto massimo con la frutta | 2-3 settimane |
| Temperatura consigliata | 18-22°C, mai sopra 25°C |

## Regole

### Fine fermentazione

**Soglia pratica**: la fermentazione è finita quando la gravità varia al massimo di **0,001 in 7 giorni**. La regola replica il metodo manuale dell'utente (una misura a settimana, due misure consecutive uguali), ma con letture continue.

**Criterio statistico** (test di equivalenza sulla pendenza):

1. Si applica solo dopo che la fermentazione è risultata **partita**, per non scambiare la fase piatta iniziale per una fermentazione finita.
2. Si considerano le letture degli ultimi **7 giorni** (finestra configurabile, sempre in giorni interi per compensare il ciclo di temperatura giorno-notte).
3. Le letture vengono aggregate in **mediane orarie**, per ridurre il rumore, i picchi dovuti al rimescolamento e la correlazione tra letture vicine.
4. Si stima la pendenza con una **regressione robusta** (Theil-Sen), con il suo intervallo di confidenza al 95%.
5. La fermentazione è finita se **l'intero intervallo di confidenza** della pendenza è compreso entro **±0,001 / 7 giorni**.
6. La condizione deve reggere per almeno **due controlli consecutivi**, per evitare avvisi dovuti a una singola oscillazione.

Perché non "pendenza compatibile con zero": con centinaia di letture l'errore diventa minuscolo e anche una coda trascurabile risulterebbe "diversa da zero" (fermentazione mai finita); con dati rumorosi l'errore è largo e una fermentazione ancora in corso risulterebbe "compatibile con zero" (falso positivo). Il test di equivalenza dichiara finito solo quando si è sicuri che la variazione sia sotto la soglia che interessa.

**FG attesa**: facoltativa e solo informativa, non blocca la dichiarazione di fine. La notifica indica se la FG raggiunta è vicina a quella attesa o se c'è una differenza da indagare.

### Avvio della fermentazione

- La partenza può richiedere da poche ore a circa due giorni.
- Avviso **"fermentazione partita"** quando la gravità inizia a scendere in modo deciso.
- Avviso **"fermentazione non ancora partita"** se dopo **72 ore** dall'inizio della cotta non si osserva alcun calo.

## Elenco degli avvisi

| Avviso | Quando scatta |
|--------|---------------|
| Fermentazione partita | La gravità inizia a scendere |
| Fermentazione non partita | Nessun calo dopo 72 ore dall'inizio della cotta |
| Fermentazione molto vigorosa | Calo di gravità molto rapido (rischio schiuma/tracimazione) |
| Promemoria frutta | Giorno 18, se la fermentazione non è ancora finita |
| Fermentazione finita | Intervallo di confidenza della pendenza entro ±0,001 / 7 giorni, per due controlli consecutivi; confronto informativo con la FG attesa |
| Temperatura alta | Temperatura sopra 25°C |
| Sensore muto | Nessuna lettura per 6 ore |
| Batteria scarica | Tensione sotto la soglia di sicurezza |

Tutte le soglie sono modificabili da configurazione, anche per singola cotta.

## Da definire nelle fasi successive

- **Soglia "molto vigorosa"**: velocità di calo da tarare con il simulatore (fase 2/4).
- **Soglia batteria**: valore di tensione da fissare in base alla batteria dell'iSpindel (fase 1/8).
- **Finestra di analisi**: confrontare con il simulatore 7 giorni e 3,5 giorni (soglia equivalente ±0,0005), per scegliere in base ai dati.
- **Fermentatore**: da acquistare, preferibilmente in vetro, 10-15 litri, con apertura abbastanza larga per l'iSpindel.
