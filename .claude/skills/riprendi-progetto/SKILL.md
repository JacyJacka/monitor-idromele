---
name: riprendi-progetto
description: Ricostruisce il contesto del progetto monitor-idromele all'inizio di una nuova sessione. Usala quando l'utente chiede di riprendere il lavoro, "dove eravamo rimasti", o all'avvio di una sessione senza contesto precedente.
---

# Riprendere il progetto monitor-idromele

Obiettivo: capire a che punto è il progetto **prima di fare qualsiasi altra cosa**, e presentarlo all'utente in modo breve, così può confermare o correggere da dove ripartire.

Questa skill **non modifica nulla**: legge, riassume e chiede.

## 1. Stato del repository

Esegui, nella cartella del progetto:

```
git fetch origin
git status -sb
git branch --show-current
git log --oneline -10 origin/main
git branch -r --no-merged origin/main
```

Annota:
- il ramo corrente e se ci sono **modifiche non salvate**;
- gli ultimi commit su `main`;
- i **rami non ancora uniti** a `main`: corrispondono a lavoro in revisione o interrotto. Per ciascuno guarda `git log --oneline origin/main..<ramo>` e `git diff --stat origin/main...<ramo>`.

## 2. Documentazione

Leggi in quest'ordine:

1. `docs/00-pianificazione.md`: tabella delle fasi con il loro stato e la sezione **"Prossimi passi"**.
2. Il documento della fase **in corso** o dell'ultima chiusa (`docs/0X-*.md`), in particolare le sezioni con le decisioni ancora aperte ("Da definire", "Decisioni ancora aperte", "Da verificare").
3. `docs/02-architettura.md`, se il prossimo passo riguarda il codice.

Leggi il codice solo se serve a chiarire un dubbio emerso dai documenti.

## 3. Verifica di coerenza

Segnala all'utente, senza correggere da solo, se:
- lo stato delle fasi nel piano non corrisponde a quello che c'è nel repository (es. una fase segnata come chiusa ma con un ramo ancora aperto);
- ci sono modifiche non salvate o rami non uniti di cui il piano non parla;
- i "Prossimi passi" sembrano superati dai commit più recenti.

## 4. Riepilogo per l'utente

Presenta, in italiano e in poche righe:

- **Dove siamo**: fasi chiuse e fase in corso.
- **Ultimo lavoro fatto**: gli ultimi commit su `main`, ed eventuali rami in revisione.
- **Decisioni aperte**: quelle annotate nei documenti.
- **Prossimo passo proposto**: il primo dei "Prossimi passi".

Poi **chiedi conferma** prima di iniziare. Quando si riparte, valgono le regole del `CLAUDE.md`: un ramo nuovo per ogni modifica, modalità plan per ogni fase di codice, revisione prima di ogni commit e push solo dopo l'ok esplicito dell'utente.
