### Git Helper
- [Wichtigste Git-Befehle zum Merken](#Wichtigste Git-Befehle zum Merken:)
- [Hinweise](#Hinweise:)
- [Git Example Worklfow](#Git Example Worklfow:)
- [Weitere Git-Befehle](#Weitere Git-Befehle:)
  - [Branches](#branches)
- [Git GUI](#Git GUI:)
- [Git Buch](https://git-scm.com/book/en/v2)
---

#### <a name='Wichtigste Git-Befehle zum Merken:'>Wichtigste Git-Befehle zum Merken:</a>



```git
git clone <link>
```

​        -> legt ein existierendes Repository lokal an (Kopie)<br>        -> den Link finde man auf GitLab/GItHub bei dem Clone-Button (nicht ssh sondern HTTP kopieren) 



```git
git add *
```
​		-> staged alle Änderungen



```git
git commit -m 'Beschreibung in a nutshell
- warum die Änderung gut war
- was genau bis wohin geändert wurde
- ...'
```
​		-> führt Änderungen im lokalen Repository durch

​		-> Mit ' kann man mehrzeilige Kommentare verfassen und der Kommentar endet erst beim nächsten '



```git
git push
```
​		-> aktualisiert das globale Repository mit lokalen Änderungen



```git
git pull
```
​		-> aktualisiert das lokale Repository mit den globalen Änderungen



```git
git status
```
​		-> informiert über den Zustand des lokalen Repositories im Vergleich zu dem globalen


---

#### <a name='Hinweise:'>Hinweise:</a>

-> Man muss sich mit der Git Bash oder der Git CMD in einem Git repository befinden, damit diese Befehle (außer git clone) funktionieren.

-> Wenn man mit der Git Bash/Git CMD in einem Git Repository ist, wird einem der Branch angezeigt und dadurch kann man es leicht erkennen.

-> Außerdem kann man in einem Ordner mit **Rechtsklick** einfach die Git Bash in diesem Ordner starten (kann hilfreich sein).

-> Keine großen Dateien Comitten/Pushen!!!

---

#### <a name='Git Example Worklfow:'>Git Example Worklfow:</a>

Max Mustermann ist in einem Team zugeteilt worden und soll mit seinen Kameraden ein Projekt mit Git auf die Beine stellen. Aber wo fängt er an? <br>Die Musterschule hat bereits ein Git-Projekt (Repository) erstellt.

0. VPN nicht vergessen. Empfehlung: Cisco AnyConnect (siehe PDF in Discord => Treffpunkt -> Pinns)

1. [Git installieren](https://git-scm.com/)

2. Git Einstellungen tätigen

   -> git config --global user.name [name]<br>-> git config --global user.email [email]

   

3. Git-Projekt auf den lokalen Rechner klonen/kopieren

   -> git clone [link]

   

4. Max Mustermann arbeitet nun am Projekt und programmiert fleißig (ganz normal so wie immer)

5. Nun möchte Max die Änderungen lokal Übernehmen.

   -> git add *<br>-> git commit -m "beschreibung"

   

6. Zu guter Letzt will er seine lokalen Änderungen mit seinem Team teilen

   -> git push

Falls das Origin Repository in der Zwischenzeit Veränderungen durchgemacht hat. Muss man sein lokales Repository zuvor aktualisieren (git pull) und anschließend seine eigenen Änderungen pushen.

---

#### <a name='Weitere Git-Befehle:'>Weitere Git-Befehle:</a>

```git 
git checkout <commit sha>
```

​		-> ladet den angegebenen Commit (so kann man frühere Versionen besuchen)

```git
git init
```
​		-> Erzeugt ein neues Git-Repository im aktuellen Ordner 

```git 
git config --global user.name <name>
```

​		-> Legt den verwendeten Namen für Git auf dem Rechner fest

​        -> ohne --global wird dieser nur für das eine Git-Projekt festgelegt

```git 
git config --global user.email <email>
```

​		->  Legt die verwendete E-Mail-Adresse für Git auf dem Rechner fest

​		-> ohne --global wird dieser nur für das eine Git-Projekt festgelegt

​		-> nur **git config user.email** zeigt die aktuell eingetragene Email für das Projekt 

```git 
git log
```

​		-> Zeigt die komplette Commit-Historie, hierbei sin einige [Optionen](https://git-scm.com/book/de/v2/Git-Grundlagen-Anzeigen-der-Commit-Historie) verfügbar

**<a name='branches'>Branching:</a>**

```git 
git branch
```

​		-> Liste aller Branches

```git 
git branch <new-branch-name>
```

​		-> Erzeugt einen neuen Branch aus dem aktuellen Branch

```git 
git branch <new-branch-name> <base-branch-name>
```

​		-> Erzeugt einen neuen Branch aus dem angegebenen Base-Branch

```git 
git checkout <branch-name>
```

​		-> Ladet den angegebenen Branch

```git 
git checkout -b <new-branch-name>
```

​		-> Erzeugt neuen branch und ladet diesen direkt

```git 
git merge <branch>
```

​		-> Merged den angegebenen Branch in den aktuellen Branch

```git 
git branch -d <branch-name>
```

​		-> Schließt den angegebenen Branch



Falls man in einen anderen Branch arbeitet und nun fertig mit seiner Arbeit ist, wechselt man erstmal zum 'master'-Branch (oder wie dieser benannt wurde) -> checkout command. Anschließend merged man den anderen Branch mit dessen Änderungen zum aktuellen Branch -> mit dem merg command.  Anschließend kann der branch geschlossen werden. 

> Denke daran, dass du zuvor deine Änderungen auf deinem Arbeitsbranch auch wirklich übernommen hast -> comitted und gepushed.

----

#### <a name='Git GUI:'>Git GUI:</a>

Keine Lust die Befehle zu merken und willst du lieber alle Änderungen klar sehen können? Genau dafür existiert die Git GUI und die Arbeit damit ist echt einfach.

**Starten**<br>Genau wie die Git Bash kann die Git GUI per Rechtsklick direkt im Wunschordner/Git-Repository geöffnet werden. Andernfalls kann man die Git GUI auch so starten und auf **Open Existing Repository** gehen (beim Startbildschirm kann man alternativ auch ein neues Repository erstellen oder ein Repository klonen).

**Bedienen**<br>Alle Änderungen sollten nun im *Unstaged Changes* Bereich links oben angezeigt werden. Falls nicht den *Rescan* Button drücken (etwa in der Mitte, der oberste Button von mehreren Buttons).<br>Nun wählt man alle Änderungen aus, welche man auch wirklich ändern möchte und staged sie indem man in der Menübar *>Commit>Stage to Commit* wählt. Und bei dem Reiter *Commit* kann man auch *Unstage From Commit* wählen um Änderungen nicht mehr zu Commiten (in den Unstaged Bereich zurück).<br>Wenn alle Änderungen gewählt/gestaged wurden, kann man die Änderungen im lokalen Repository ausführen (committen). Hierzu den *Commit*-Button drücken.<br>Falls ihr eure Änderungen auch mit dem Original Repository aktualisieren wollt, drückt den *Push*-Button (das kann auch zu einem beliebig späteren Zeitpunkt erfolgen).<br><br>Wurde etwas im Original Repository (nicht lokal) geändert und ihr wollt diese Änderungen (weil ihr beispielsweise Pushen wollt), so müssen 2 Schritten getan werden.<br>1. *> Remote > Fetch from*<br>2.*> Merge > Local Merge*<br>(Tatsächlich macht das der git pull Befehl intern auch)

**Worklflow Beispiel**<br>1. Git GUI an gewünschtem Ort öffnen (wo Projektordner erscheinen soll) <br>    -> mit Rechtsklick und Git GUI öffnen<br>2. *Clone Existing Repository* wählen<br>    -> Source Directory: HTTP-Link von Repository<br>    -> Target Directory: Ordnerpfad/Ordner, wo noch nicht exstitiert, wo das Projekt rein kommt<br>3. Nun kann man fleißig arbeiten (Dateien erstellen, bearbeiten, löschen)<br>4. Auf *Rescan* drücken<br>5. Alle Änderungen, die man ändern möchte, stagen (in *Commit* Reiter)<br>6. Commit Nachricht schreiben und auf *Commit* drücken<br>7. Repository aktualisieren (nicht immer nötig)<br>    -> *Remote > Fetch From*<br>    -> *Merge > Local Merge*<br>8. Auf *Push* drücken

**Weitere Features**

- Unter *> Repository* kann man sich einen oder alle Branches Visualisieren lassen (drücke auf *Visualize ...*)

- Unter *> Tools > Add...* kann man Git Befehle hinzufügen, welche man auf Knopfdruck durchführen kann<br>        -> *Name* ist nur ein beliebiger Name<br>        -> *Command* ist dann der git Befehl (git add * oder git pull ...)
- Unter *> Branch* kann man neue Branches erstellen oder auch einen checkout in andere Branches durchführen

**Hinweise**

- Keine großen Dateien Comitten/Pushen!!!
-  Wenn push nicht funktioniert, muss das Repository aktualisiert werden.<br>    1. *Remote > Fetch From*<br>    2. *Merge > Local Merge*
-  man kann auch gerne eine Kombi mit Git Bash und Git GUI wählen, denn beide haben Vor- und Nachteile
- Unter *> Repository > Git Bash* kann die Git Bash schnell geöffnet werden
- *git pull* Befehl bei *Tools* erzeugen, welcher einiges erleichtert (siehe komplizieren Weg oben)

**Wichtige Shortcuts**

- Ctrl+T/Ctrl+U: Stage/unstage selected file
- Ctrl+I: Stage all files (asks if you want to add new files if there are any)
- Ctrl+J: Revert changes
- Ctrl+Enter: Commit
- Ctrl+P: Push
- Ctrl+M: Local Merge
- F5: Rescan

---



