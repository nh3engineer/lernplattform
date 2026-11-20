"""Versand der Auswertungs-PDFs per E-Mail (SMTP).

Faellt SMTP aus oder ist nicht konfiguriert, wird das PDF lokal gespeichert,
damit die Plattform auch ohne Mailserver nutzbar bleibt.
"""
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

from . import config


def _save_local(pdf_bytes: bytes, dateiname: str) -> str:
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    pfad = os.path.join(config.RESULTS_DIR, dateiname)
    with open(pfad, "wb") as f:
        f.write(pdf_bytes)
    return pfad


def _build_message(empfaenger: str, betreff: str, text: str,
                   pdf_bytes: bytes, dateiname: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = config.MAIL_FROM
    msg["To"] = empfaenger
    msg["Subject"] = betreff
    msg.set_content(text)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf",
                       filename=dateiname)
    return msg


def versende_auswertung(auswertung: dict, pdf_bytes: bytes) -> dict:
    """
    Sendet das PDF an den Pruefling UND (als Kopie) an die Lehrperson.
    Rueckgabe: dict mit Status-Infos.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sichere_fach = auswertung["fach"].lower()
    dateiname = f"auswertung_{sichere_fach}_{ts}.pdf"

    pruefling = (auswertung.get("email") or "").strip()
    lehrkraft = config.INSTRUCTOR_EMAIL

    ergebnis = {"versendet": [], "gespeichert": None, "fehler": []}

    if not config.mail_configured():
        pfad = _save_local(pdf_bytes, dateiname)
        ergebnis["gespeichert"] = pfad
        ergebnis["fehler"].append(
            "SMTP nicht konfiguriert - PDF lokal gespeichert statt versendet.")
        return ergebnis

    betreff = (f"Pr&uuml;fungsauswertung {auswertung['fach']} "
               f"{auswertung['stufe_name']} - {auswertung['prozent']:.0f} %")
    # Betreff ohne HTML-Entities fuer echte Mail
    betreff = betreff.replace("&uuml;", "ue")

    text_pruefling = (
        f"Hallo {auswertung.get('name') or ''},\n\n"
        f"im Anhang findest du die Auswertung deiner Pruefung:\n"
        f"  Fach:   {auswertung['fach']}\n"
        f"  Stufe:  {auswertung['stufe_name']}\n"
        f"  Thema:  {auswertung['thema_name']}\n"
        f"  Ergebnis: {auswertung['punkte']}/{auswertung['max_punkte']} Punkte "
        f"({auswertung['prozent']:.0f} %), Note {auswertung['note']}\n\n"
        f"Hinweis: Eine Kopie dieser Auswertung wurde an die Lehrperson uebermittelt.\n\n"
        f"Viel Erfolg beim Weiterlernen!\nDeine Lernplattform"
    )

    text_lehrkraft = (
        f"Automatische Kopie einer Pruefungsauswertung.\n\n"
        f"  Pruefling: {auswertung.get('name') or '-'} <{pruefling or '-'}>\n"
        f"  Fach:   {auswertung['fach']}\n"
        f"  Stufe:  {auswertung['stufe_name']}\n"
        f"  Thema:  {auswertung['thema_name']}\n"
        f"  Ergebnis: {auswertung['punkte']}/{auswertung['max_punkte']} Punkte "
        f"({auswertung['prozent']:.0f} %), Note {auswertung['note']}\n"
        f"  Datum: {auswertung.get('datum','')}\n"
    )

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            if config.SMTP_USE_TLS:
                server.starttls(context=context)
            server.login(config.SMTP_USER, config.SMTP_PASS)

            # An Lehrkraft (immer)
            if lehrkraft:
                server.send_message(_build_message(
                    lehrkraft, "[Kopie] " + betreff, text_lehrkraft, pdf_bytes, dateiname))
                ergebnis["versendet"].append(lehrkraft)

            # An Pruefling (wenn gueltige Adresse)
            if pruefling and "@" in pruefling:
                server.send_message(_build_message(
                    pruefling, betreff, text_pruefling, pdf_bytes, dateiname))
                ergebnis["versendet"].append(pruefling)
    except Exception as e:  # noqa: BLE001
        # Bei Fehler zur Sicherheit lokal ablegen
        pfad = _save_local(pdf_bytes, dateiname)
        ergebnis["gespeichert"] = pfad
        ergebnis["fehler"].append(f"SMTP-Fehler: {e}")

    return ergebnis
