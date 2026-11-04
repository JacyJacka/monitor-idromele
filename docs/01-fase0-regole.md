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

- La fermentazione è **finita** quando la gravità varia al massimo di **0,001 in 7 giorni**.
- La regola replica il metodo manuale dell'utente (una misura a settimana, due misure consecutive uguali), ma con letture continue.
- La **FG attesa** è facoltativa e solo informativa: non blocca la dichiarazione di fine. La notifica indica se la FG raggiunta è vicina a quella attesa o se c'è una differenza da indagare.

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
| Fermentazione finita | Variazione ≤ 0,001 in 7 giorni, con confronto informativo con la FG attesa |
| Temperatura alta | Temperatura sopra 25°C |
| Sensore muto | Nessuna lettura per 6 ore |
| Batteria scarica | Tensione sotto la soglia di sicurezza |

Tutte le soglie sono modificabili da configurazione, anche per singola cotta.

## Da definire nelle fasi successive

- **Soglia "molto vigorosa"**: velocità di calo da tarare con il simulatore (fase 2/4).
- **Soglia batteria**: valore di tensione da fissare in base alla batteria dell'iSpindel (fase 1/8).
- **Filtro dei disturbi** da rimescolamento: tecnica di filtraggio da scegliere in fase 4.
- **Fermentatore**: da acquistare, preferibilmente in vetro, 10-15 litri, con apertura abbastanza larga per l'iSpindel.
