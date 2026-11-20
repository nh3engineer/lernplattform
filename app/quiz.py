"""Laden der Fragen und Bewertung der Pruefungen."""
import json
import os
import random

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "fragen.json",
)


def lade_daten() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fach_liste() -> list:
    """Baum fuer die Auswahl im Frontend: Faecher -> Stufen -> Themen."""
    daten = lade_daten()
    out = []
    for fach_key, fach in daten["faecher"].items():
        stufen = []
        for stufe_key, stufe in sorted(fach["stufen"].items()):
            themen = []
            for thema_key, thema in stufe["themen"].items():
                themen.append({
                    "key": thema_key,
                    "name": thema["name"],
                    "anzahl": len(thema["fragen"]),
                })
            stufen.append({"key": stufe_key, "name": stufe["name"], "themen": themen})
        out.append({"key": fach_key, "name": fach["name"], "stufen": stufen})
    return out


def hole_thema(fach_key: str, stufe_key: str, thema_key: str):
    daten = lade_daten()
    fach = daten["faecher"].get(fach_key)
    if not fach:
        return None
    stufe = fach["stufen"].get(stufe_key)
    if not stufe:
        return None
    thema = stufe["themen"].get(thema_key)
    if not thema:
        return None
    return {
        "fach_name": fach["name"],
        "stufe_name": stufe["name"],
        "thema_name": thema["name"],
        "fragen": thema["fragen"],
    }


def erzeuge_pruefung(fach_key, stufe_key, thema_key, anzahl=0):
    """Gibt die (ggf. zufaellig gemischten) Fragen OHNE Loesungen zurueck."""
    thema = hole_thema(fach_key, stufe_key, thema_key)
    if thema is None:
        return None
    fragen = list(thema["fragen"])
    random.shuffle(fragen)
    if anzahl and anzahl > 0:
        fragen = fragen[:anzahl]
    public = []
    for q in fragen:
        pub = {"id": q["id"], "typ": q["typ"], "frage": q["frage"]}
        if q["typ"] == "mc":
            # Optionen mischen, Zuordnung ueber Original-Index bleibt in loesung
            opts = list(enumerate(q["optionen"]))
            random.shuffle(opts)
            pub["optionen"] = [{"idx": i, "text": t} for i, t in opts]
        else:
            pub["einheit"] = q.get("einheit", "")
        public.append(pub)
    return {
        "fach_name": thema["fach_name"],
        "stufe_name": thema["stufe_name"],
        "thema_name": thema["thema_name"],
        "fragen": public,
    }


def _mc_text(frage: dict, idx) -> str:
    try:
        return frage["optionen"][int(idx)]
    except (ValueError, TypeError, IndexError):
        return "(keine Antwort)"


def bewerte(fach_key, stufe_key, thema_key, antworten: dict) -> dict:
    """
    antworten: {frage_id: wert}  (wert = Options-Index bei mc, Zahl/Text bei num)
    Gibt die vollstaendige Auswertung inkl. Note zurueck.
    """
    thema = hole_thema(fach_key, stufe_key, thema_key)
    if thema is None:
        return None
    by_id = {q["id"]: q for q in thema["fragen"]}

    details = []
    punkte = 0
    # Nur Fragen bewerten, die auch gestellt wurden (in antworten vorhanden).
    gestellte_ids = [fid for fid in antworten.keys() if fid in by_id]
    if not gestellte_ids:
        gestellte_ids = list(by_id.keys())

    for fid in gestellte_ids:
        q = by_id[fid]
        gegeben = antworten.get(fid, None)
        richtig = False
        if q["typ"] == "mc":
            deine_text = _mc_text(q, gegeben)
            loesung_text = q["optionen"][q["loesung"]]
            try:
                richtig = int(gegeben) == q["loesung"]
            except (ValueError, TypeError):
                richtig = False
        else:  # num
            loesung_text = f"{q['loesung']} {q.get('einheit','')}".strip()
            deine_roh = (str(gegeben).strip() if gegeben is not None else "")
            deine_text = deine_roh or "(keine Antwort)"
            try:
                wert = float(deine_roh.replace(",", "."))
                tol = q.get("toleranz", 0.001)
                richtig = abs(wert - float(q["loesung"])) <= tol
            except (ValueError, TypeError):
                richtig = False

        if richtig:
            punkte += 1
        details.append({
            "frage": q["frage"],
            "richtig": richtig,
            "deine_antwort": deine_text,
            "loesung": loesung_text,
            "erklaerung": q.get("erklaerung", ""),
        })

    max_punkte = len(details)
    prozent = (punkte / max_punkte * 100) if max_punkte else 0.0
    note = _note(prozent)

    return {
        "fach": thema["fach_name"],
        "stufe_name": thema["stufe_name"],
        "thema_name": thema["thema_name"],
        "punkte": punkte,
        "max_punkte": max_punkte,
        "prozent": prozent,
        "note": note,
        "details": details,
    }


def _note(prozent: float) -> str:
    """Oesterreichisches Notenschema (1 Sehr gut ... 5 Nicht genuegend)."""
    if prozent >= 89:
        return "1 (Sehr gut)"
    if prozent >= 76:
        return "2 (Gut)"
    if prozent >= 63:
        return "3 (Befriedigend)"
    if prozent >= 50:
        return "4 (Genuegend)"
    return "5 (Nicht genuegend)"
