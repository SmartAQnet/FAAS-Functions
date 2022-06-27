# OpenFAAS Umgebung und Entwicklung

## Quickstart

1.  Docker muss installiert sein.
2.  Installieren des Kommandozeilentools
    [faas-cli](https://github.com/openfaas/faas-cli):
    `curl -sSL https://cli.openfaas.com | sudo sh` (Unter Windows können
    [Binaries von Github](https://github.com/openfaas/faas-cli/releases)
    ("faas-cli.exe") eingesetzt werden)
3.  Verbinden mit dem [TECO
    VPN](https://intranet.teco.edu/projects/admin/wiki/VPN) , wenn noch
    keine Verbindung zum TECO-Netzwerk vorhanden ist.
4.  Login an Docker Registry: `docker login registry.teco.edu`
    (\[\[Docker-Registry\|credentials\]\])
5.  Login an Faas Gateway:
    `faas-cli login --gateway https://api.smartaq.net:8081 --password admin`
6.  Klonen des FAAS repos:
    `git clone https://github.com/SmartAQnet/FAAS-Functions.git`
7.  Verzeichnis wechseln: `cd FAAS-Functions/`
8.  Pullen des python 3 Templates:
    `faas-cli template store pull python3-http-debian`
9.  Erstellen einer neuen Python 3 Funktion mit Namen "test": faas-cli
    new test ---lang python3-http-debian
    ---gateway=https://api.smartaq.net:8081
    ---prefix=registry.teco.edu/smartaqnet/faas
10. Verändern von `test/handler.py` zu was auch immer die Funktion
    leisten soll. Bibliotheken müssen in
    [requirements.txt](https://pip.readthedocs.io/en/1.1/requirements.html#the-requirements-file-format)
    eingetragen werden.
11. Bauen, Pushen und Ausrollen der Funktion:
    `faas-cli -f test.yml up -a` (Beachte, dass `up` ein Shortcut für
    die folgenden drei Befehle ist: `build`, `push` und `deploy`)
12. Die öffentliche Funktion wird unter
    https://api.smartaq.net/function/test aufrufbar sein (auch wenn die
    Kommandozeile etwas von api.smartaq.net:8081sagt, was aber nur im
    TECO-Netzwerk funktioniert)

Note:\
Die Logs der Funktion können hier eingesehen werden:
`faas-cli -f test.yml logs --gateway=https://api.smartaq.net:8081 test`\
Information dazu, was alles möglich ist innerhalb der Funktion (Parsen
von Parametern, Setzen von headern,...) steht hier::
https://github.com/openfaas-incubator/python-flask-template#example-usage\
Im UI kann nachgeschaut werden, ob die Funktion "Ready" ist:
https://admin:admin@api.smartaq.net:8081/ui/\
Wenn eine Funktion potentiell lange dauert, sollten die Timeout-Optionen
wie im Abschnitt "Erstellen einer neuen Funktion" angepasst werden.\
Für weitere Probleme:
https://docs.openfaas.com/deployment/troubleshooting/

## Einrichten einer lokalen OpenFAAS Umgebung

Im \[\[SmartAQnet-Cluster\]\] läuft eine [OpenFFAS Instanz im
Docker-Swarm-Mode](https://docs.openfaas.com/deployment/docker-swarm/)

Eingerichtet werden kann eine ähnliche Instanz am eigenen PC wie folgt:\
1. Installieren von Docker (+Compose)\
2. Erstellen eines 1-Node-Docker-Swarm: `docker swarm init`\
3. Holen der neusten Release-Version von OpenFAAS auf
[Github](https://github.com/openfaas/faas/releases):
`wget https://github.com/openfaas/faas/archive/0.18.2.tar.gz`\
4. Entpacken: `tar -xf 0.18.2.tar.gz && cd faas-0.18.2/`\
5. Ausführen des Deployment-Skrips: `./deploy_stack.sh`

Wichtig: Die angezeigten Anmeldedaten sind wichtig und müssen notiert
werden.

Für FAAS im TECO-Swarm gelten folgende Anmeldedaten:\
username: admin\
password: admin

## Erstellen einer neuen Funktion

Diese Anleitung erlaubt es eine Funktion lokal zu entwickeln. Eine
vollständigere Anleitung ist auf der [OpenFAAS
Website](https://docs.openfaas.com/cli/templates/) zu finden.

1\. Installieren des Kommandozeilentools
[faas-cli](https://github.com/openfaas/faas-cli):
`curl -sSL https://cli.openfaas.com | sudo sh` (Unter Windows können
[Binaries von Github](https://github.com/openfaas/faas-cli/releases)
("faas-cli.exe") eingesetzt werden)

2\. Auswählen eines Templates: `faas-cli template store list` zeigt eine
Liste von verfügbaren Templates\
Eine Beispiel-Ausgabe ist:

    NAME                     SOURCE             DESCRIPTION
    csharp                   openfaas           Classic C# template
    dockerfile               openfaas           Classic Dockerfile template
    go                       openfaas           Classic Golang template
    java8                    openfaas           Classic Java 8 template
    node                     openfaas           Classic NodeJS 8 template
    php7                     openfaas           Classic PHP 7 template
    python                   openfaas           Classic Python 2.7 template
    python3                  openfaas           Classic Python 3.6 template
    ruby                     openfaas           Classic Ruby 2.5 template
    node10-express           openfaas-incubator Node.js 10 powered by express template
    ruby-http                openfaas-incubator Ruby 2.4 HTTP template
    python27-flask           openfaas-incubator Python 2.7 Flask template
    python3-flask            openfaas-incubator Python 3.6 Flask template
    python3-http             openfaas-incubator Python 3.6 with Flask and HTTP
    node8-express            openfaas-incubator Node.js 8 powered by express template
    golang-http              openfaas-incubator Golang HTTP template
    golang-middleware        openfaas-incubator Golang Middleware template
    python3-debian           openfaas-incubator Python 3.6 Debian template
    powershell-template      openfaas-incubator Powershell Core Ubuntu:16.04 template
    powershell-http-template openfaas-incubator Powershell Core HTTP Ubuntu:16.04 template
    rust                     booyaa             Rust template
    crystal                  tpei               Crystal template
    csharp-httprequest       distantcam         C# HTTP template
    vertx-native             pmlopes            Eclipse Vert.x native image template
    swift                    affix              Swift 4.2 Template
    lua53                    affix              Lua 5.3 Template
    vala                     affix              Vala Template
    vala-http                affix              Non-Forking Vala Template
    quarkus-native           pmlopes            Quarkus.io native image template
    perl-alpine              tmiklas            Perl language template based on Alpine image
    node10-express-service   openfaas-incubator Node.js 10 express.js microservice template
    crystal-http             koffeinfrei        Crystal HTTP template

**Templates aus dem `openfaas-incubator` sollten bevorzugt werden.**\
Templates aus der Quelle `openfaas-incubator` verwenden ein neueres
[Backend](https://docs.openfaas.com/architecture/watchdog/) im Vergleich
zu denen aus `openfaas`, welches wesentlich mehr Funktionalität anbietet
(z.B. Setzen von HTTP-Response-Headern in Funktionen).

3\. Holen eines Templates:
`faas-cli template store pull node10-express`\
4. Erstellen einer Funktion auf Basis des Templates "node10-express" mit
dem namen "test":
`faas-cli new test --lang node10-express --gateway=https://api.smartaq.net:8081 --prefix=registry.teco.edu/smartaqnet/faas`\
5. Anpassen der Funktionseigenschaften:\
Eine Funktion darf nur eine bestimmte Zeit brauchen, bis sie beendet
wird.\
Es empfiehlt sich die Datei test.yml wie folgt anzupassen:

    functions:
      test:
        [...]
        environment:
            read_timeout: 2m
            write_timeout: 2m
            exec_timeout: 2m

\
Damit werden mehrere Timeouts auf zwei Minuten gesetzt. [Weitere
Umgebungsvariablen](https://github.com/openfaas-incubator/of-watchdog/blob/master/README.md#configuration)
und [Konfigurationsmöglichkeiten für
Funktionen](https://docs.openfaas.com/reference/yaml/) (z.B. RAM Limits,
Scaling, ...)\
6. Schreiben der eigentlichen Funktion. Dazu gibt es gute Informationen
im Git-Repository des Templates.

## Schreiben von Python-Funktionen

~~Python-Images im FAAS-Incubator basieren auf Alpine-Linux. Das ist
eine schlechte Kombination für Python, da die Build-Zeiten um ein
Vielfaches höher sind als z.B. bei Debian. (Siehe:
https://pythonspeed.com/articles/alpine-docker-python/)~~

~~Deshalb steht ein Template für Python-Funktionen hier bereit:
https://github.com/SmartAQnet/FAAS-Functions/tree/master/template/python3-http-debian-slim~~

Inzwischen gibt es ein Template für Python 3 Funktionen auf Basis von
Debian Slim. Eine Funktion kann wie im Abschnitt "Quickstart" erstellt
werden.

Anschließend muss nur der Code in der "handler.py"-Datei angepasst und
entsprechende Abhängigkeiten in der requirements.txt eingetragen werden.

## Testen einer Funktion (lokal)

Die Funktion kann so geschrieben werden, dass sie gleichzeitig lokal
ausgeführt werden kann, indem sinnvolle Default-Werte für Variablen
gewählt werden, die später durch ein Request ausgefüllt werden.\
Es empfiehlt sich außerdem, ein lokales OpenFAAS-Gateway zu benutzen,
wenn man die Funktion in einer OpenFAAS Umgebung testen möchte. Siehe
dazu "Einrichten der OpenFAAS Umgebung".\
Bei Port-Konflikten kann der lokale Gateway-Port angepasst werden, indem
der Gateway-Port in der `docker-compose.yml` nach dem 4. Schritt
angepasst wird. Zum Beispiel wird der Port 8081 verwendet:

    gateway:
            ports:
                - 8081:8080

Nun kann die Funktion "test" aus dem oberen Beispiel "Erstellen einer
neuen Funktion" wie folgt installiert werden:\
1. Bauen des Docker-Abbilds: `faas-cli -f test.yml build`\
2. Anmelden an lokaler instanz:
`echo -n <PASSWORD aus "Einrichten einer lokalen OpenFAAS Umgebung"> | faas-cli login --username=admin --password-stdin --gateway "http://127.0.0.1:8081"`\
3. Deployment auf lokaler Instanz:
`faas-cli -f test.yml deploy --gateway "http://127.0.0.1:8081"`

Die Funktion ist unter http://127.0.0.1:8081/function/test verfügbar.
Unter http://127.0.0.1:8081/ui/ kann man den Status der Funktion sehen.
Die Anmeldedaten sind die aus dem Punkt "Einrichten der OpenFAAS
Umgebung"

## Deployment einer Funktion im TECO-Cluster

Das UI des Gateways ist unter
https://admin:admin@api.smartaq.net:8081/ui/ abrufbar.

1.  Login an Docker Registry: `docker login registry.teco.edu`
    (\[\[Docker-Registry\|credentials\]\])
2.  Anmelden am entfernten Gateway:
    `faas-cli login --gateway https://api.smartaq.net:8081 --password admin`
    (nur aus dem TECO Netzwerk möglich)
3.  Bauen des Docker-Abbilds: `faas-cli -f test.yml build`\
    Es ist wichtig darauf zu achten, dass in der `.yml`-Datei folgende
    Einträge stehen:
        provider:
          [...]
          gateway: https://api.smartaq.net:8081
        functions:
          [NAME_DER_FUNKTION]:
            [..]
            image: registry.teco.edu/smartaqnet/faas/[NAME_DER_FUNKTION]:latest

    \
    Diese Einträge sind automatisch vorhanden, wenn eine Funktion wie im
    Abschnitt "Quickstart" erstellt wird.
4.  Pushen des Docker-Abbilds der Funktion zur TECO-Docker-Registry:
    `faas-cli -f test.yml push`
5.  Deployment an entfernter Instanz `faas-cli -f test.yml deploy -a`

Die letzten drei Befehle lassen sich als `faas-cli -f test.yml up -a`
abkürzen.

# OpenFAAS-Funktionen

Aktuell im Deployment:

## aggregator

URL: https://api.smartaq.net/function/aggregator

Simple aggregation function that will take a normal frost path and query
to a list list of observations which it will aggregate and return. Set
the additional query parameter \$aggregate=x where x is the aggregation
interval in minutes. Example:

https://api.smartaq.net/function/aggregator/Datastreams('saqn%3Ads%3Aae03f57')/Observations?\$filter=phenomenonTime%20gt%202020-06-23T15:46:15.000Z%20and%20phenomenonTime%20lt%202020-06-24T15:46:15.000Z&\$orderby=phenomenonTime%20desc&\$top=10000&\$aggregate=60

Important: The top parameter will prevent following nextLinks and simply
ignore them. If the top parameter is not present, the aggregator will
follow nextLinks.

## aggregate-observations

URL: https://api.smartaq.net/function/aggregate-observations

Takes a frost query, finds all Observation-Arrays within and aggregates
observations in each array. The resulting response has the format of a
FROST-Server/SensorThings response.\
You are responsible to invoke this functions with sensible requests. For
example: Aggregating over arrays of Observations where one array
contains Observations from multiple Datastreams does not make sense if
the results have different units / observed properties.

### Parameter

aggregate-observations/ **[]{style="resultAggregator;"}** -
**[]{style="locationAggregator;"}** - **[]{style="timeAggregator;"}** -
**[]{style="durationPerChunk;"}** / **[]{style="frostServerQuery;"}**

  Parameter            Possible Values                  Example                                                                                                                                                       Definition
  -------------------- -------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------
  resultAggregator     "none", "mean"                   "none"                                                                                                                                                        Defines how results are aggregated. "mean" is the arithmetic mean. None takes the result of the first Observation in the chunk.
  locationAggregator   "none", "mean"                   "none"                                                                                                                                                        Defines how locations are aggregated. "mean" is the mean of the coordinate vector. None takes the location of the first Observation in the chunk.
  timeAggregator       "none", "mean"                   "none"                                                                                                                                                        Defines how phenomenonTime is aggregated. "mean" is the mean of all time points within one chunk. None takes the time of the first Observation in the chunk.
  durationPerChunk     ISO 8601 duration format         "PT20M" \[= 20 Minutes\]                                                                                                                                      Observation arrays are split in chunks of this size and then aggregated.
  frostServerQuery     FROST-Server-Pfad/Query-String   "Observations?\$filter=phenomenonTime gt 2019-11-18T12:50:20.000Z and phenomenonTime lt 2019-11-19T12:50:20.000Z&\$orderby=phenomenonTime desc&\$top=10000"   Query sent to the FROST-Server

### Function specifics

Execution timeout is set to 2 minutes.\
The Cache-Control header field from the client is echoed in the server
response (or set to no-cache as default value) to support a possibly
later installed proxy server.
