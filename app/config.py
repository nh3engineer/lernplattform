"""
Konfiguration der Lernplattform.

Alle sensiblen Werte (E-Mail-Zugangsdaten) werden ueber Umgebungsvariablen
gesetzt und NICHT im Code gespeichert. Siehe .env.example / README.md.
"""
import os


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "ja", "on")


# --- Allgemein ---------------------------------------------------------------
HOST = os.environ.get("LP_HOST", "0.0.0.0")
PORT = int(os.environ.get("LP_PORT", "5000"))
SECRET_KEY = os.environ.get("LP_SECRET_KEY", "bitte-im-produktivbetrieb-aendern")

# --- Uebungsmodus (ohne PDF/Mail) -------------------------------------------
# Anzahl Fragen beim Ueben; danach werden sofort die Loesungen angezeigt.
UEBUNG_FRAGEN = int(os.environ.get("LP_UEBUNG_FRAGEN", "5"))

# --- Pruefungsmodus (mit PDF/Mail) ------------------------------------------
# Richtzeit einer Pruefung in Minuten (Timer im Browser, Auto-Abgabe bei 0).
PRUEFUNG_DAUER_MIN = int(os.environ.get("LP_PRUEFUNG_DAUER_MIN", "20"))
# Anzahl Fragen pro Pruefung (auf ca. die Richtzeit ausgelegt).
PRUEFUNG_FRAGEN = int(os.environ.get("LP_PRUEFUNG_FRAGEN", "12"))

# --- E-Mail-Versand (SMTP) ---------------------------------------------------
SMTP_HOST = os.environ.get("LP_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("LP_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("LP_SMTP_USER", "")          # z.B. hechtl.office@gmail.com
SMTP_PASS = os.environ.get("LP_SMTP_PASS", "")          # Gmail App-Passwort (NICHT das normale PW)
SMTP_USE_TLS = _get_bool("LP_SMTP_USE_TLS", True)
MAIL_FROM = os.environ.get("LP_MAIL_FROM", SMTP_USER or "lernplattform@localhost")

# Lehrkraft-Adresse, die IMMER eine Kopie jeder Auswertung erhaelt.
INSTRUCTOR_EMAIL = os.environ.get("LP_INSTRUCTOR_EMAIL", "hechtl.office@gmail.com")

# Wenn SMTP nicht konfiguriert ist, werden die PDFs lokal gespeichert statt versendet.
RESULTS_DIR = os.environ.get(
    "LP_RESULTS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ergebnisse"),
)


def mail_configured() -> bool:
    return bool(SMTP_USER and SMTP_PASS)
