"""Laden der Fragen und Bewertung von Uebungen/Pruefungen."""
import json
import os
import random

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "fragen.json",
)

ALLE = "__alle__"   # Spezialwert: alle Themen einer Schulstufe


def lade_daten() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _index(daten: dict) -> dict:
    """Globaler Index: frage_id -> {frage, fach_name, stufe_name, thema_name}."""
    idx = {}
    for fach in daten["faecher"].values():
        for stufe in fach["stufen"].values():
            for thema in stufe["themen"].values():
                for q in thema["fragen"]:
                    idx[q["id"]] = {
                        "frage": q,
                        "fach_name": fach["name"],
                        "stufe_name": stufe["name"],
                        "thema_name": thema["name"],
                    }
    return idx


def fach_liste() -> list:
    """Baum fuer die Auswahl im Frontend: Faecher -> Stufen -> Themen."""
    daten = lade_daten()
    out = []
    for fach_key, fach in daten["faecher"].items():
        stufen = []
        for stufe_key, stufe in sorted(fach["stufen"].items()):
            themen = [{"key": tk, "name": t["name"], "anzahl": len(t["fragen"])}
                      for tk, t in stufe["themen"].items()]
            gesamt = sum(x["anzahl"] for x in themen)
            stufen.append({"key": stufe_key, "name": stufe["name"],
                           "themen": themen, "gesamt": gesamt})
        out.append({"key": fach_key, "name": fach["name"], "stufen": stufen})
    return out


def _sammle_fragen(fach_key, stufe_key, thema_key):
    """Liefert (kontext, fragenliste) fuer ein Thema oder die ganze Stufe."""
    daten = lade_daten()
    fach = daten["faecher"].get(fach_key)
    if not fach:
        return None, None
    stufe = fach["stufen"].get(stufe_key)
    if not stufe:
        return None, None

    if thema_key == ALLE:
        fragen = []
        for thema in stufe["themen"].values():
            fragen.extend(thema["fragen"])
        thema_name = "Alle Themen der Schulstufe"
    else:
        thema = stufe["themen"].get(thema_key)
        if not thema:
            return None, None
        fragen = list(thema["fragen"])
        thema_name = thema["name"]

    kontext = {"fach_name": fach["name"], "stufe_name": stufe["name"],
               "thema_name": thema_name}
    return kontext, fragen


def erzeuge_pruefung(fach_key, stufe_key, thema_key, anzahl):
    """Gibt (ggf. zufaellig gemischte) Fragen OHNE Loesungen zurueck."""
    kontext, fragen = _sammle_fragen(fach_key, stufe_key, thema_key)
    if kontext is None:
        return None
    fragen = list(fragen)
    random.shuffle(fragen)
    if anzahl and anzahl > 0:
        fragen = fragen[:anzahl]

    public = []
    for q in fragen:
        pub = {"id": q["id"], "typ": q["typ"], "frage": q["frage"]}
        if q["typ"] == "mc":
            opts = list(enumerate(q["optionen"]))
            random.shuffle(opts)
            pub["optionen"] = [{"idx": i, "text": t} for i, t in opts]
        else:
            pub["einheit"] = q.get("einheit", "")
        public.append(pub)

    return {
        "fach_name": kontext["fach_name"],
        "stufe_name": kontext["stufe_name"],
        "thema_name": kontext["thema_name"],
        "fragen": public,
    }


def _mc_text(frage, idx):
    try:
        return frage["optionen"][int(idx)]
    except (ValueError, TypeError, IndexError):
        return "(keine Antwort)"


def bewerte(antworten: dict, kontext: dict = None) -> dict:
    """
    Bewertet anhand des globalen Frage-Index (funktioniert auch bei
    gemischten Pruefungen ueber mehrere Themen).
    antworten: {frage_id: wert}
    kontext (optional): {fach_name, stufe_name, thema_name} fuer die Anzeige.
    """
    idx = _index(lade_daten())
    gestellte = [fid for fid in antworten.keys() if fid in idx]
    if not gestellte:
        return None

    details = []
    punkte = 0
    for fid in gestellte:
        q = idx[fid]["frage"]
        gegeben = antworten.get(fid)
        if q["typ"] == "mc":
            deine_text = _mc_text(q, gegeben)
            loesung_text = q["optionen"][q["loesung"]]
            try:
                richtig = int(gegeben) == q["loesung"]
            except (ValueError, TypeError):
                richtig = False
        else:  # num
            loesung_text = f"{q['loesung']} {q.get('einheit','')}".strip()
            roh = (str(gegeben).strip() if gegeben is not None else "")
            deine_text = roh or "(keine Antwort)"
            try:
                wert = float(roh.replace(",", "."))
                richtig = abs(wert - float(q["loesung"])) <= q.get("toleranz", 0.001)
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

    # Kontext aus der ersten Frage ableiten, falls nicht uebergeben
    if not kontext:
        erste = idx[gestellte[0]]
        kontext = {"fach_name": erste["fach_name"],
                   "stufe_name": erste["stufe_name"],
                   "thema_name": erste["thema_name"]}

    return {
        "fach": kontext["fach_name"],
        "stufe_name": kontext["stufe_name"],
        "thema_name": kontext["thema_name"],
        "punkte": punkte,
        "max_punkte": max_punkte,
        "prozent": prozent,
        "note": _note(prozent),
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
