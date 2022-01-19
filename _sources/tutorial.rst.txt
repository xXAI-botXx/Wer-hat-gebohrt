Tutorial
^^^^^^^^
This library is programmed for distinguish drilling persons.

To start the application, you need a setup with following points:

* drilldriver and drillcapture programs
* wired drill
* wood for drilling
* at least 2 persons
* our library
* python3 installed
* all modules in the requirements.txt (see below)

.. code-block:: none

    ###### Requirements without Version Specifiers ######
    pandas
    matplotlib
    sklearn
    ttkthemes
    pyyaml
    tsfresh
    pillow
    webbrowser

    ###### Requirements with Version Specifiers ######
    numpy <= 1.20

    ###### Linux System need to install ######
    # Tkinter
    # sudo apt-get install python3-tk 

    # And Pillow Tk
    # sudo apt-get install python3-pil.imagetk


If the setup is ready, you have to call the run-function in following module:

:ref:`gui`

See the RUN.py for an exemplary call.

.. hint::

    Dabei muss sichergestellt sein, dass kein weiterer Drilldriver läuft. Um das zu tun, muss einfach der Output in der Konsole/Terminal überprüft werden und es muss **MCCUDP found!** dastehen. Fall dort etwas steht wie **MCCUDP Acquiring...** muss die Anwendung geschlossen werden und folgende Schritte befolgt werden:
    
    1. Im Terminal **killall MCCUDP** eingeben
    2. Erneut **killall MCCUDP** im Terminal eingeben
    3. Anwendung mit **python3 RUN.py** starten
    4. Anwendung schließen
    5. Anwendung erneut starten und nun funktioniert alles wieder

