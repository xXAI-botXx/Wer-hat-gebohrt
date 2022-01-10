#### Beschreibung dieser Datei:

Hier werden verschiedene Informationen und Planungen über die Software gesammelt.

#### Table of Contents:

- [Analyse](#analyse)
  - [Use-Case-Diagramm](#usecase)
  - [Klassendiagramm](#klassendiagramm)
- [Design](#design)
  - [Zustandsbeschreibung](#zustandsbeschreibung)
---

---

## <a name='analyse'>Analyse</a>

---

---
#### <a name='usecase'>Use-Case-Diagramm + Beschreibung</a>

> In progress...



#### <a name='klassendiagramm'>Klassendiagramm (Analyse)</a>

> In progress...




---

---

## <a name='design'>Design</a>

---

---

#### <a name='zustandsbeschreibung'>Zustände der Software</a>

- Bohrstil erkennen

  - Bohren Person 1 + Namenseingabe + Bohrdaten zurücksetzen

    -> Es existiert keine Bohrobergrenze nur eine Untergrenze

    -> Rein theoretisch können sich die Personen mit dem Bohren abwechseln 

    -> Daten Speicherung

  - Switchen zu Person 2 und andersherum

  - Bohren Person 2 + Namenseingabe + Bohrdaten zurücksetzen

  - Lernen von den Daten + springt zu 'Bohrung zur Identifikation' Zustand

- Bohrung zur Identifikation

  - x oder mehr Bohrungen

    -> Keine Obergrenze (?)

  - Rückkehr zu 'Bohrstil erkennen'

  - Start der Identifikation/Klassifikation

    -> springt zu 'Identifikation'-Zustand

- Identifikation

  - Ausgabe des Resultats
  - Neustart
  - Rückkehr zu 'Bohrung zur Identifikation'-Zustand



---

