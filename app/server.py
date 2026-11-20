"""Flask-Webserver der Lernplattform."""
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
import io

from . import config, quiz
from .pdf_report import build_pdf
from .mailer import versende_auswertung


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    @app.route("/")
    def index():
        return render_template("index.html",
                               mail_aktiv=config.mail_configured(),
                               instructor=config.INSTRUCTOR_EMAIL)

    @app.route("/api/faecher")
    def api_faecher():
        return jsonify(quiz.fach_liste())

    @app.route("/api/pruefung")
    def api_pruefung():
        fach = request.args.get("fach", "")
        stufe = request.args.get("stufe", "")
        thema = request.args.get("thema", "")
        p = quiz.erzeuge_pruefung(fach, stufe, thema, config.FRAGEN_PRO_PRUEFUNG)
        if p is None:
            return jsonify({"fehler": "Thema nicht gefunden"}), 404
        return jsonify(p)

    @app.route("/api/abgabe", methods=["POST"])
    def api_abgabe():
        data = request.get_json(force=True, silent=True) or {}
        fach = data.get("fach", "")
        stufe = data.get("stufe", "")
        thema = data.get("thema", "")
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        antworten = data.get("antworten", {}) or {}

        if not email or "@" not in email:
            return jsonify({"fehler": "Bitte eine gueltige E-Mail-Adresse eingeben."}), 400

        auswertung = quiz.bewerte(fach, stufe, thema, antworten)
        if auswertung is None:
            return jsonify({"fehler": "Thema nicht gefunden"}), 404

        auswertung["name"] = name
        auswertung["email"] = email
        auswertung["datum"] = datetime.now().strftime("%d.%m.%Y %H:%M")

        pdf_bytes = build_pdf(auswertung)
        mail_status = versende_auswertung(auswertung, pdf_bytes)

        return jsonify({
            "punkte": auswertung["punkte"],
            "max_punkte": auswertung["max_punkte"],
            "prozent": round(auswertung["prozent"], 1),
            "note": auswertung["note"],
            "details": auswertung["details"],
            "mail": {
                "versendet": mail_status["versendet"],
                "gespeichert": mail_status["gespeichert"],
                "fehler": mail_status["fehler"],
            },
        })

    @app.route("/api/pdf", methods=["POST"])
    def api_pdf():
        """Erzeugt das PDF erneut zum direkten Download (ohne erneuten Mailversand)."""
        data = request.get_json(force=True, silent=True) or {}
        auswertung = quiz.bewerte(
            data.get("fach", ""), data.get("stufe", ""),
            data.get("thema", ""), data.get("antworten", {}) or {})
        if auswertung is None:
            return jsonify({"fehler": "Thema nicht gefunden"}), 404
        auswertung["name"] = (data.get("name") or "").strip()
        auswertung["email"] = (data.get("email") or "").strip()
        auswertung["datum"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        pdf_bytes = build_pdf(auswertung)
        return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                         as_attachment=True, download_name="auswertung.pdf")

    return app


app = create_app()
