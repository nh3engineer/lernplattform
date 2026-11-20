#!/usr/bin/env python3
"""Startet die Lernplattform.

Aufruf:  python run.py
Danach im Browser oeffnen:  http://localhost:5000
"""
import os


def _lade_env(pfad=".env"):
    """Einfacher .env-Loader (ohne Zusatzpaket)."""
    if not os.path.exists(pfad):
        return
    with open(pfad, "r", encoding="utf-8") as f:
        for zeile in f:
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#") or "=" not in zeile:
                continue
            key, _, val = zeile.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            # Vorhandene echte Umgebungsvariablen haben Vorrang
            os.environ.setdefault(key, val)


_lade_env()

from app import config          # noqa: E402  (nach .env-Load importieren)
from app.server import app      # noqa: E402

if __name__ == "__main__":
    print("=" * 60)
    print(" Lernplattform Physik & Mathematik")
    print(f" Oeffne im Browser:  http://localhost:{config.PORT}")
    if not config.mail_configured():
        print(" ! E-Mail-Versand NICHT konfiguriert - PDFs werden lokal")
        print(f"   gespeichert in: {config.RESULTS_DIR}")
        print("   (zum Aktivieren siehe README.md / .env.example)")
    else:
        print(f" E-Mail-Versand aktiv ueber {config.SMTP_HOST}")
        print(f" Kopie an Lehrperson: {config.INSTRUCTOR_EMAIL}")
    print("=" * 60)
    app.run(host=config.HOST, port=config.PORT, debug=False)
