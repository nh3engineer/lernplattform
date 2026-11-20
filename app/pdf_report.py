"""Erzeugt ein PDF mit der Pruefungsauswertung."""
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="LPTitle", fontSize=18, leading=22,
                              spaceAfter=6, textColor=colors.HexColor("#1a3c6e")))
    styles.add(ParagraphStyle(name="LPSub", fontSize=10, leading=14,
                              textColor=colors.HexColor("#555555")))
    styles.add(ParagraphStyle(name="LPQ", fontSize=10, leading=14, spaceBefore=4))
    styles.add(ParagraphStyle(name="LPSmall", fontSize=8.5, leading=11,
                              textColor=colors.HexColor("#666666")))
    return styles


def build_pdf(auswertung: dict) -> bytes:
    """
    auswertung erwartet die Keys:
      fach, stufe_name, thema_name, name, email, datum,
      punkte, max_punkte, prozent, note,
      details: Liste von dicts mit frage, richtig(bool), deine_antwort, loesung, erklaerung
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title="Pruefungsauswertung")
    s = _styles()
    story = []

    story.append(Paragraph("Lernplattform &ndash; Pr&uuml;fungsauswertung", s["LPTitle"]))
    story.append(Paragraph(
        f"{auswertung['fach']} &middot; {auswertung['stufe_name']} &middot; {auswertung['thema_name']}",
        s["LPSub"]))
    story.append(Spacer(1, 8))

    kopf = [
        ["Name / Pr&uuml;fling:", auswertung.get("name") or "&ndash;"],
        ["E-Mail:", auswertung.get("email") or "&ndash;"],
        ["Datum:", auswertung.get("datum", datetime.now().strftime("%d.%m.%Y %H:%M"))],
    ]
    kopf_tbl = Table([[Paragraph(k, s["LPSmall"]), Paragraph(v, s["LPQ"])] for k, v in kopf],
                     colWidths=[40 * mm, 130 * mm])
    kopf_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(kopf_tbl)
    story.append(Spacer(1, 10))

    # Ergebnis-Box
    farbe = colors.HexColor("#1e8e3e") if auswertung["prozent"] >= 50 else colors.HexColor("#c5221f")
    erg = Table([[
        Paragraph(f"<b>{auswertung['punkte']} / {auswertung['max_punkte']} Punkte</b>", s["LPQ"]),
        Paragraph(f"<b>{auswertung['prozent']:.0f} %</b>", s["LPQ"]),
        Paragraph(f"<b>Note: {auswertung['note']}</b>", s["LPQ"]),
    ]], colWidths=[57 * mm, 57 * mm, 56 * mm])
    erg.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, farbe),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f8ff")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(erg)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Detailauswertung</b>", s["LPQ"]))
    story.append(Spacer(1, 4))

    for i, d in enumerate(auswertung["details"], start=1):
        mark = "&#10003;" if d["richtig"] else "&#10007;"
        mark_col = colors.HexColor("#1e8e3e") if d["richtig"] else colors.HexColor("#c5221f")
        frage_p = Paragraph(f"<b>{i}. {d['frage']}</b>", s["LPQ"])
        deine = Paragraph(f"Deine Antwort: {d['deine_antwort']}", s["LPSmall"])
        loes = Paragraph(f"Richtige Antwort: {d['loesung']}", s["LPSmall"])
        erkl = Paragraph(f"<i>{d.get('erklaerung','')}</i>", s["LPSmall"])
        zelle = [frage_p, deine, loes, erkl]
        row = Table([[Paragraph(f"<font color='{mark_col.hexval()}'><b>{mark}</b></font>", s["LPQ"]), zelle]],
                    colWidths=[10 * mm, 160 * mm])
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(row)

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "Automatisch erstellt von der Lernplattform. Eine Kopie dieser Auswertung "
        "wurde an die Lehrperson &uuml;bermittelt.", s["LPSmall"]))

    doc.build(story)
    return buf.getvalue()
