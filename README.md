# Lernplattform Physik &amp; Mathematik

Eine portable Web-Lernplattform für **Physik** und **Mathematik**, bei der
Prüfungen nach **Fach** und **Schulstufe** (HTL 1.–5. Klasse) sowie
Themengebiet zusammengestellt werden. Die Auswertung erfolgt **automatisch**,
und das Ergebnis-PDF wird per E-Mail an den Prüfling geschickt – mit einer
automatischen **Kopie an die Lehrperson**.

Die Anwendung läuft lokal auf jedem Rechner mit Python (Windows, macOS, Linux).

---

## Funktionen

- Auswahl: Fach → Schulstufe → Themengebiet
- Fragetypen: Multiple Choice (Antwortoptionen werden gemischt) und numerische
  Eingaben (mit Toleranz)
- Automatische Bewertung inkl. Prozent und österreichischer Note (1–5)
- Detailauswertung mit richtiger Antwort und kurzer Erklärung je Frage
- PDF-Erstellung der Auswertung
- E-Mail-Versand an Prüfling **und** Lehrperson (`hechtl.office@gmail.com`)
- Transparenter Hinweis im Formular, dass die Lehrperson eine Kopie erhält
- Ohne konfigurierten Mailserver werden die PDFs lokal im Ordner
  `ergebnisse/` abgelegt, sodass alles auch offline testbar ist

---

## Installation

Voraussetzung: Python 3.10 oder neuer.

```bash
cd lernplattform
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Starten

```bash
python run.py
```

Dann im Browser öffnen: <http://localhost:5000>

Soll die Plattform im lokalen Netz (anderer Rechner) erreichbar sein, läuft der
Server bereits auf `0.0.0.0` – andere Geräte erreichen ihn über
`http://<IP-des-Rechners>:5000`.

---

## E-Mail-Versand aktivieren

Standardmäßig ist kein Mailversand eingerichtet (die PDFs landen dann im Ordner
`ergebnisse/`). Zum echten Versand:

1. Datei `.env.example` nach `.env` kopieren.
2. Zugangsdaten eintragen. Für **Gmail** ist ein **App-Passwort** nötig
   (nicht das normale Passwort):
   - Google-Konto → Sicherheit → Bestätigung in zwei Schritten aktivieren
   - → App-Passwörter → neues Passwort für „Mail" erzeugen
   - dieses 16-stellige Passwort als `LP_SMTP_PASS` eintragen
3. Server neu starten.

Die wichtigsten Variablen (siehe `.env.example`):

| Variable | Bedeutung |
|---|---|
| `LP_SMTP_HOST` | SMTP-Server (Gmail: `smtp.gmail.com`) |
| `LP_SMTP_PORT` | Port (Gmail: `587`) |
| `LP_SMTP_USER` | Absender-Konto |
| `LP_SMTP_PASS` | App-Passwort |
| `LP_INSTRUCTOR_EMAIL` | Adresse für die Kopie (`hechtl.office@gmail.com`) |

Die Datei `.env` enthält Zugangsdaten und ist über `.gitignore` vom Commit
ausgeschlossen.

---

## Datenschutz-Hinweis

Jeder Prüfling sieht vor der Abgabe den Hinweis, dass das Ergebnis-PDF neben der
eigenen Adresse auch an die Lehrperson übermittelt wird. Diese Transparenz ist
bewusst so gewählt (DSGVO-konform) – funktional erhält die Lehrperson jede
Auswertung.

---

## Fragen erweitern

Alle Fragen stehen in `data/fragen.json`. Struktur:

```
faecher → <fach> → stufen → <1..5> → themen → <thema> → fragen → [ ... ]
```

Fragetypen:

- `"typ": "mc"` – Multiple Choice: `optionen` (Liste), `loesung` (Index der
  richtigen Option, 0-basiert)
- `"typ": "num"` – numerisch: `loesung` (Zahl), `toleranz`, optional `einheit`

Jede Frage kann eine `erklaerung` enthalten, die in der Auswertung erscheint.
Nach dem Bearbeiten der JSON-Datei genügt ein Neustart des Servers.
