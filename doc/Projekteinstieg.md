# Projekt 1 AKI: Wer hat gebohrt?

Bitte dokumentieren Sie die einzelnen Punkte in Gitlab in diesem Markdown-Dokument.

Zu Punkt 6: Stellen Sie große Teilschritte (Punkt 4) inkl. der Milestones bitte in einem [Gantt-Chart](https://de.wikipedia.org/wiki/Gantt-Diagramm) dar.
Die detaillierten Teilschritte des MVPs können Sie gleich als Issues in Gitlab anlegen (wo möglich mit Zuweisung von Zuständigkeit $\rightarrow$ Schritt 7).

## 1. GEMEINSAME VISION
-   Wie sieht das Endergebnis aus?
-   Was kann Ihr System?
-   Wie wird damit interagiert werden?  

(Tipp: Stellen Sie sich die Situation vor, die entsteht, wenn ein Nutzer mit dem von Ihnen entwickelten System interagiert.
Welche Schritte werden in welcher Reihenfolge durchgeführt?
Welche Erwartungen hat der Nutzer?
Wie wird er reagieren?
Wie interagiert er mit dem System?)

<!-- Ihre gemeinsame Vision -->

<!-- Use-Case-Diagramm adden -->

<!-- Zustandsdiagramm adden -->

Vorgehen:

1. 2 Personen bohren x mal auf dem selben Material
2. Einer der beiden Personen bohrt ein weiteres mal
3. On the fly Identifizieren, wer von den beiden gebohrt hat

Eine Software mit grafischer Oberfläche oder per Konsolenausgabe wird den Probanden suggerieren, was zu tun ist und was die Software gerade macht.

Die Software soll flexibel gestaltet werden. So soll man nach dem Klassifizieren, auch wieder bohren können. Außerdem sollen Prozesse ab brechbar sein. Falls Jemand nochmals neu bohren möchte.



## 2. KOMPONENTEN DES SYSTEMS
Aus welchen Komponenten besteht Ihr System?
Denken Sie sowohl über die Software- vs. Hardware-Komponenten nach als auch darüber, aus welchen Teilkomponenten die Software besteht.

<!-- Die Komponenten des Systems -->

### Hardware

- Bohrer
- Bohraufsatz
- Sensoren
  - Sound
  - Stromstärke
  - Spannung
- Bohrmaterial
- Computer auf dem die Software läuft + der mit dem Bohrer verbunden ist



### Software

- Bohraufnahme + Labeln
- Datenmanipulation
- Daten Lernen / Modell trainieren + abspeichern (in Variable oder als File)
- Neue Daten Predicten (trainiertes Modell verwenden)
- Interface (grafisch oder text), über den gesamten Prozess



---

## 3. MACHINE LEARNING AUFGABE
Überlegen Sie nun, welche Machine Learning Aufgabe Ihrem Projekt zugrunde liegt.
Um welche Art von Machine Learning-Problem handelt es sich (supervised / unsupervised, Regression / Clustering / Klassifikation / …)?
Welche Daten werden benötigt?

<!-- Machine Learning Aufgabe -->

Da die Daten gelabelt und von dem Algorithmus gelernt werden sollen (der Algorithmus soll das grundlegende Muster eines Bohrstils erkennen), handelt es sich um eine Supervised Learning Problem. Außerdem soll der Algorithmus einen neuen Dateneintrag zu einem von 2 Kategorien (Menschen) zuordnen, also ist es ein Klassifikations-Problem.

## 4. IDENTIFIKATION VON TEILSCHRITTEN
Welche Teilschritte müssen angegangen werden, damit Sie Ihr Ziel erreichen?
(Denken Sie hier sowohl an die ML-Komponente als auch die anderen Software-Komponenten)

<!-- Identifikation von Teilschritten -->

- Organisatorisches

  - Vorgehensmodell
  - Analysemodelle
  - Designmodelle
  - Ordnerstruktur / Teamworkflow

  

- Datenbeschaffung

  - Live-Übertragung (?) 

  

- Data Exploration

  - Visualisierung
  - Feature-Extraction ?

  

- Data Preparation

  - Akku-Leistung Filterung



- KI-Modelling

  - Besten KI-Algorithmus für dieses Problem finden
  - Hyperparameter optimiert einstellen

  

- Automatisierung

  - Ein Softwarefluss (Kontrollsoftware mit Interface)

    -> Input und Output für User



- Evaluierung



- Optional Goals
  - GUI
  - Live Datenübertragung



## 5. MINIMUM VIABLE PRODUCT (MVP)
Gibt es ein „Minimum Viable Product“ (zu Deutsch etwa „minimal brauchbares oder existenzfähiges Produkt“) und wie sieht dieses in Ihrem Fall aus?
Welche Teilschritte sind erforderlich, um diese erste lauffähige Version mit Grundfunktionen zu erreichen?

<!-- Minimum Viable Product (MVP) -->

#### MVP:

- Aufgenommene Daten (manuell koordiniert) werden prepariert (Feature_Extraction)
- Ein Model lässt sich durch zuvor preparierte Daten trainieren und abspeichern
- Laden des Models und klassifizieren eines neuen und ebenfalls preparierten Datensatzes

- Keine GUI/UI -> sondern nur Jupyter Lab's
  - Ergebnisse werden abgelesen und mündlich bekanntgegeben
  - Inputs werden manuell eingegeben
- viele Daten/Bohrungen der 2 Personen



#### Teilschritte:

(Hinweis: In Module denken, wie Notes in Knime nur etwas größer)

- Data Preparation



- Model-training

  - AI-Model training
  - AI-Model saving

  

- Klassifizierung

  - AI-Model loading
  - Klassifizierung

  

-> Zu Beginn muss noch eine Data Exploration durchgeführt werden



## 6. PROJEKTPLAN
Stellen Sie einen Projektplan auf.
Während Sie unter 4 die erforderlichen Teilschritte identifiziert haben, geht es nun um eine zeitliche Planung.
Dabei handelt es sich um eine Grobplanung für den Gesamtablauf und eine detailliertere Planung für das Erreichen des MVPs.

<!-- Projektplan -->

#### Grober Zeitplan für Gesamtablauf:

| ID   | Name                             | Definition of Done                                           | Zeitrahmen           |
| ---- | -------------------------------- | ------------------------------------------------------------ | ------------------- |
| 1    | Bohrdaten | Daten (Messungen+Metadaten) auf dem Rechner verfügbar -> mindestends 20 Messungen pro Person<br>(Eventuell noch mehr Personen) | 29.10.2021    |
| 2    | Data Understanding               | Die Daten wurden exploriert, verstanden und es wurden Ideen zur Data-Preparation gesammelt | 05.11.2021 |
| 3    | Data Preparation | Die Daten wurden so vorbereitet und manipuliert, damit man sie sinnvoll für das Projekt verwenden kann | 26.11.2021 |
| 4 | KI-Model trainiert und klassifiziert | Es wurde ein KI-Modell problemorientiert ausgwählt, trainiert und abgespeichert. Zudem kann man dieses Modell laden und predicten lassen | 03.12.2021 |
| 6 | Evaluierung | Accuracy-Score über 50% | 10.12.2021 |
| 7 | Verbesserung des Ergebnisses | Accuracy-Score über 75% | 29.12.2021 |
| 8 | Vollendung des Ergebnisses | Accuracy-Score über 90% | 14.01.2022 |
| 9 | Automatisierung | Prediction funktioniert mit weniger Daten und in einem Rutsch (+ Bohrdaten on the fly übernommen?) | 29.12.2021 |
| 10 | UI/GUI | Benutzer können mit der Software interagieren: Ausgaben werden darüber getätigt, transparente Anzeigen über Softwarestatus (zu 80% sicher, dass es x ist, ich lerne gerade...) | 07.01.2022 |





#### Detaillierter Zeitplan zum erreichen des MVP:



Bemerkung des Erstellers: Aktuell sind das eigentlich aufeinanderaufbauende Schritte. Eventuell sollte man das noch ändern. Man könnte die Schritte noch genauer spezifizieren (?)



## 7. TEAM-ORGANISATION
Teilen Sie die als nächstes anstehenden Aufgaben untereinander auf.
Wer kümmert sich um was?
Wann treffen Sie sich für die nächste Absprache?
(Denken Sie dabei auch daran, dass jede/r in einigen Wochen eine kurze Präsentation machen sollte zu einem „_Expertenthema_“, d.h. einem Thema, um das er/sie sich in der Anfangsphase besonders gekümmert hat)

<!-- Team Organisation -->

**Welche Themen/Rollen gibt es?**<br>- Feature Extraction / Data Preparation<br>- AI-Model training and saving<br>- AI-Model loading and classification<br>- Modulerweiterung

Tipp: Nicht in festen Rollen denken. Alle werden miteinander interagieren und die Grenzen sind überlagernd / nicht eindeutig. Es geht nur darum, wer sich grob um was kümmert. Wer also was programmiert, ...



-> Fragen nach 4.ter Rolle und ob bisherige Rollen ok sind
