"""Flask-Webserver der Lernplattform."""
import io
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file

from . import config, quiz
from .pdf_report import build_pdf
from .mailer import versende_auswertung


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            mail_aktiv=config.mail_configured(),
            instructor=config.INSTRUCTOR_EMAIL,
            uebung_fragen=config.UEBUNG_FRAGEN,
            pruefung_fragen=config.PRUEFUNG_FRAGEN,
            pruefung_dauer=config.PRUEFUNG_DAUER_MIN,
        )

    @app.route("/api/faecher")
    def api_faecher():
        return jsonify(quiz.fach_liste())

    @app.route("/api/pruefung")
    def api_pruefung():
        fach = request.args.get("fach", "")
        stufe = request.args.get("stufe", "")
        thema = request.args.get("thema", "")
        modus = request.args.get("modus", "pruefung")

        if modus == "uebung":
            anzahl = config.UEBUNG_FRAGEN
        else:
            modus = "pruefung"
            anzahl = config.PRUEFUNG_FRAGEN

        p = quiz.erzeuge_pruefung(fach, stufe, thema, anzahl)
        if p is None:
            return jsonify({"fehler": "Thema nicht gefunden"}), 404

        p["modus"] = modus
        if modus == "pruefung":
            p["dauer_min"] = config.PRUEFUNG_DAUER_MIN
        return jsonify(p)

    @app.route("/api/abgabe", methods=["POST"])
    def api_abgabe():
        data = request.get_json(force=True, silent=True) or {}
        modus = data.get("modus", "pruefung")
        antworten = data.get("antworten", {}) or {}
        kontext = {
            "fach_name": data.get("fach_name", ""),
            "stufe_name": data.get("stufe_name", ""),
            "thema_name": data.get("thema_name", ""),
        }
        if not all(kontext.values()):
            kontext = None

        auswertung = quiz.bewerte(antworten, kontext)
        if auswertung is None:
            return jsonify({"fehler": "Keine gueltigen Antworten uebermittelt."}), 400

        antwort = {
            "modus": modus,
            "punkte": auswertung["punkte"],
            "max_punkte": auswertung["max_punkte"],
            "prozent": round(auswertung["prozent"], 1),
            "note": auswertung["note"],
            "details": auswertung["details"],
        }

        # Uebungsmodus: nur Loesungen anzeigen, KEIN PDF/Mail.
        if modus == "uebung":
            return jsonify(antwort)

        # Pruefungsmodus: E-Mail erforderlich, PDF erzeugen + versenden.
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        if not email or "@" not in email:
            return jsonify({"fehler": "Bitte eine gueltige E-Mail-Adresse eingeben."}), 400

        auswertung["name"] = name
        auswertung["email"] = email
        auswertung["datum"] = datetime.now().strftime("%d.%m.%Y %H:%M")

        pdf_bytes = build_pdf(auswertung)
        mail_status = versende_auswertung(auswertung, pdf_bytes)
        antwort["mail"] = {
            "versendet": mail_status["versendet"],
            "gespeichert": mail_status["gespeichert"],
            "fehler": mail_status["fehler"],
        }
        return jsonify(antwort)

    @app.route("/api/pdf", methods=["POST"])
    def api_pdf():
        """Erzeugt das PDF erneut zum direkten Download (ohne erneuten Mailversand)."""
        data = request.get_json(force=True, silent=True) or {}
        kontext = {
            "fach_name": data.get("fach_name", ""),
            "stufe_name": data.get("stufe_name", ""),
            "thema_name": data.get("thema_name", ""),
        }
        if not all(kontext.values()):
            kontext = None
        auswertung = quiz.bewerte(data.get("antworten", {}) or {}, kontext)
        if auswertung is None:
            return jsonify({"fehler": "Keine gueltigen Antworten uebermittelt."}), 400
        auswertung["name"] = (data.get("name") or "").strip()
        auswertung["email"] = (data.get("email") or "").strip()
        auswertung["datum"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        pdf_bytes = build_pdf(auswertung)
        return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                         as_attachment=True, download_name="auswertung.pdf")

    return app


app = create_app()
