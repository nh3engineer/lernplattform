#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator fuer data/fragen.json.

Numerische Loesungen werden hier in Python BERECHNET, damit keine
Rechenfehler entstehen. Zum Erweitern einfach Fragen ergaenzen und
`python data/build_fragen.py` ausfuehren.
"""
import json
import math
import os

g = 9.81          # Erdbeschleunigung m/s^2
c = 2.998e8       # Lichtgeschwindigkeit m/s


def MC(frage, optionen, loesung, erkl=""):
    return {"typ": "mc", "frage": frage, "optionen": optionen,
            "loesung": loesung, "erklaerung": erkl}


def NUM(frage, loesung, toleranz, einheit="", erkl=""):
    return {"typ": "num", "frage": frage, "loesung": round(float(loesung), 6),
            "toleranz": toleranz, "einheit": einheit, "erklaerung": erkl}


def T(name, *fragen):
    return {"name": name, "fragen": list(fragen)}


# =====================================================================
#  MATHEMATIK
# =====================================================================
mathematik = {"name": "Mathematik", "stufen": {}}

mathematik["stufen"]["1"] = {"name": "HTL 1. Klasse", "themen": {
  "termumformungen": T("Termumformungen & Grundrechenarten",
    MC("Vereinfache: 3a + 5a - 2a", ["6a", "10a", "a", "8a"], 0, "3+5-2 = 6, also 6a."),
    MC("Multipliziere aus: 2(x + 4)", ["2x + 4", "2x + 8", "x + 8", "2x + 6"], 1, "2·x + 2·4 = 2x + 8."),
    MC("Erste binomische Formel: (a + b)² =", ["a² + b²", "a² + ab + b²", "a² + 2ab + b²", "a² - 2ab + b²"], 2, "a² + 2ab + b²."),
    NUM("Berechne den Wert des Terms 4x - 3 für x = 5.", 4*5-3, 0.001, "", "4·5 - 3 = 17."),
    NUM("Berechne: (-3)² + 2·(-4)", (-3)**2 + 2*(-4), 0.001, "", "9 + (-8) = 1."),
  ),
  "lineare-gleichungen": T("Lineare Gleichungen",
    NUM("Löse nach x: 2x + 6 = 14", (14-6)/2, 0.001, "", "2x = 8, x = 4."),
    NUM("Löse nach x: 5x - 7 = 3x + 5", (5+7)/(5-3), 0.001, "", "2x = 12, x = 6."),
    NUM("Löse nach x: x/3 = 4", 4*3, 0.001, "", "x = 12."),
    MC("Welche Umformung ist bei Gleichungen erlaubt?",
       ["Beide Seiten mit 0 multiplizieren", "Auf beiden Seiten dieselbe Zahl addieren",
        "Nur eine Seite verändern", "Durch 0 dividieren"], 1, "Äquivalenzumformung auf beiden Seiten."),
    NUM("Löse nach x: 3(x - 2) = 9", 9/3 + 2, 0.001, "", "x - 2 = 3, x = 5."),
  ),
  "bruchrechnung": T("Bruchrechnung",
    NUM("Berechne: 1/2 + 1/4 (als Dezimalzahl)", 1/2 + 1/4, 0.001, "", "0,5 + 0,25 = 0,75."),
    NUM("Berechne: 2/3 · 3/4 (Dezimalzahl)", (2/3)*(3/4), 0.001, "", "6/12 = 0,5."),
    NUM("Berechne: (3/4) : (1/2) (Dezimalzahl)", (3/4)/(1/2), 0.001, "", "3/4 · 2/1 = 1,5."),
    MC("Wie kürzt man 6/8?", ["2/4", "3/4", "4/6", "1/2"], 1, "Durch 2 kürzen: 3/4."),
  ),
  "potenzen-wurzeln": T("Potenzen & Wurzeln",
    NUM("Berechne: 2⁵", 2**5, 0.001, "", "2·2·2·2·2 = 32."),
    MC("Potenzgesetz: a³ · a² =", ["a⁵", "a⁶", "a¹", "a⁹"], 0, "Exponenten addieren: a^(3+2)=a⁵."),
    NUM("Berechne: √144", math.sqrt(144), 0.001, "", "12² = 144."),
    MC("Was bedeutet a⁻²?", ["-a²", "1/a²", "2/a", "a·(-2)"], 1, "Negativer Exponent: Kehrwert, 1/a²."),
    NUM("Berechne: 10³ · 10² (als Zehnerpotenz-Ergebnis)", 10**5, 1, "", "10^(3+2)=10⁵=100000."),
  ),
  "geometrie": T("Flächen & Volumina",
    NUM("Fläche eines Rechtecks mit a = 5 cm, b = 3 cm?", 5*3, 0.01, "cm²", "A = a·b = 15 cm²."),
    NUM("Fläche eines Kreises mit r = 2 cm? (gerundet)", math.pi*2**2, 0.1, "cm²", "A = π·r² ≈ 12,57 cm²."),
    NUM("Umfang eines Kreises mit r = 5 cm? (gerundet)", 2*math.pi*5, 0.1, "cm", "U = 2πr ≈ 31,42 cm."),
    NUM("Volumen eines Würfels mit a = 3 cm?", 3**3, 0.01, "cm³", "V = a³ = 27 cm³."),
    MC("Die Fläche eines Dreiecks berechnet man mit", ["a·b", "(g·h)/2", "π·r²", "a²"], 1, "A = Grundlinie·Höhe/2."),
  ),
  "einheiten": T("Maßeinheiten & Umrechnen",
    NUM("Wandle 2,5 km in Meter um.", 2.5*1000, 0.1, "m", "1 km = 1000 m → 2500 m."),
    NUM("Wandle 1500 g in kg um.", 1500/1000, 0.001, "kg", "1000 g = 1 kg → 1,5 kg."),
    NUM("Wandle 3 h in Minuten um.", 3*60, 0.1, "min", "1 h = 60 min → 180 min."),
    NUM("Wie viele cm² sind 1 m²?", 10000, 1, "cm²", "1 m = 100 cm → (100)² = 10 000 cm²."),
  ),
}}

mathematik["stufen"]["2"] = {"name": "HTL 2. Klasse", "themen": {
  "quadratische-gleichungen": T("Quadratische Gleichungen",
    MC("Lösungsformel für ax² + bx + c = 0:", ["(-b ± √(b²-4ac))/(2a)", "(-b ± √(b²+4ac))/(2a)",
       "(b ± √(b²-4ac))/a", "(-b ± √(4ac-b²))/(2a)"], 0, "Große Lösungsformel."),
    NUM("Eine Lösung von x² - 5x + 6 = 0 ist x = 2. Zweite Lösung?", 3, 0.001, "", "Vieta: 2·x₂=6 → x₂=3."),
    NUM("Berechne die Diskriminante von x² - 4x + 4 = 0.", (-4)**2 - 4*1*4, 0.001, "", "D = b²-4ac = 0."),
    MC("Was bedeutet D < 0?", ["Zwei reelle Lösungen", "Eine reelle Lösung",
       "Keine reelle Lösung", "Unendlich viele"], 2, "Keine reellen Lösungen."),
    NUM("Positive Lösung von x² = 49?", 7, 0.001, "", "√49 = 7."),
  ),
  "lineare-funktionen": T("Lineare Funktionen",
    MC("Steigung von y = 3x + 2?", ["2", "3", "3x", "5"], 1, "k = 3."),
    NUM("Nullstelle (x-Wert) von y = 2x - 6?", 6/2, 0.001, "", "2x-6=0 → x=3."),
    NUM("y-Achsenabschnitt (d) von y = -4x + 7?", 7, 0.001, "", "d = 7."),
    NUM("Steigung durch P(0|1) und Q(2|5)?", (5-1)/(2-0), 0.001, "", "k = Δy/Δx = 4/2 = 2."),
    MC("Zwei Geraden sind parallel, wenn", ["die d gleich sind", "die k gleich sind",
       "sie sich schneiden", "k·d = 0"], 1, "Gleiche Steigung k."),
  ),
  "quadratische-funktionen": T("Quadratische Funktionen",
    MC("Der Graph von y = x² ist eine", ["Gerade", "Parabel", "Hyperbel", "Kreis"], 1, "Parabel."),
    NUM("Scheitel-x von y = x² - 6x + 5 (x = -b/2a)?", 6/(2*1), 0.001, "", "x = 6/2 = 3."),
    NUM("Eine Nullstelle von y = x² - 9 (positiv)?", 3, 0.001, "", "x²=9 → x=±3."),
    MC("Öffnet y = -2x² + 3 nach", ["oben", "unten", "links", "rechts"], 1, "a<0 → nach unten."),
  ),
  "trigonometrie": T("Trigonometrie im Dreieck",
    MC("sin(α) =", ["Ankathete/Hypotenuse", "Gegenkathete/Hypotenuse",
       "Gegenkathete/Ankathete", "Hypotenuse/Gegenkathete"], 1, "Gegenkathete/Hypotenuse."),
    NUM("Berechne sin(30°) (Dezimal).", math.sin(math.radians(30)), 0.01, "", "= 0,5."),
    NUM("Hypotenuse bei Katheten 3 und 4?", math.hypot(3,4), 0.01, "", "√(9+16)=5."),
    NUM("Berechne cos(60°) (Dezimal).", math.cos(math.radians(60)), 0.01, "", "= 0,5."),
    MC("tan(α) =", ["sin·cos", "sin/cos", "cos/sin", "1/sin"], 1, "tan = sin/cos."),
  ),
  "vektoren": T("Vektoren (2D)",
    NUM("Länge des Vektors (3; 4)?", math.hypot(3,4), 0.01, "", "√(3²+4²)=5."),
    MC("Summe (1;2) + (3;1) =", ["(4;3)", "(3;2)", "(4;2)", "(2;1)"], 0, "Komponentenweise: (4;3)."),
    NUM("Skalarprodukt (2;3)·(1;4)?", 2*1+3*4, 0.01, "", "2·1+3·4 = 14."),
    MC("Zwei Vektoren stehen normal (senkrecht), wenn ihr Skalarprodukt",
       ["= 1 ist", "= 0 ist", "negativ ist", "= Länge ist"], 1, "Skalarprodukt = 0."),
  ),
  "gleichungssysteme": T("Lineare Gleichungssysteme",
    NUM("Aus x + y = 10 und x - y = 2: x = ?", (10+2)/2, 0.001, "", "Addition: 2x=12 → x=6."),
    NUM("Aus x + y = 10 und x - y = 2: y = ?", (10-2)/2, 0.001, "", "y = 4."),
    MC("Ein LGS mit 2 Gleichungen und 2 Unbekannten hat i.d.R.",
       ["keine Lösung", "genau eine Lösung", "immer unendlich viele", "drei Lösungen"], 1, "I.d.R. genau eine."),
  ),
}}

mathematik["stufen"]["3"] = {"name": "HTL 3. Klasse", "themen": {
  "differentialrechnung": T("Differentialrechnung",
    MC("Ableitung von f(x) = x³?", ["3x²", "x²", "3x", "x⁴/4"], 0, "Potenzregel: 3x²."),
    NUM("f'(2) für f(x) = x²?", 2*2, 0.001, "", "f'(x)=2x → 4."),
    MC("Ableitung von sin(x)?", ["-sin(x)", "cos(x)", "-cos(x)", "tan(x)"], 1, "cos(x)."),
    NUM("f'(1) für f(x) = 3x² + 2x?", 6*1+2, 0.001, "", "f'(x)=6x+2 → 8."),
    MC("Bei einem Extremum gilt", ["f(x)=0", "f'(x)=0", "f''(x)=1", "f'(x)=1"], 1, "f'(x)=0."),
  ),
  "kurvendiskussion": T("Kurvendiskussion",
    NUM("Nullstelle von f(x) = 2x - 8?", 8/2, 0.001, "", "2x-8=0 → x=4."),
    MC("Ein Wendepunkt liegt vor, wenn", ["f'(x)=0", "f''(x)=0 und VZW", "f(x)=0", "f'(x)=1"], 1, "f''(x)=0 mit Vorzeichenwechsel."),
    MC("f''(x) > 0 bedeutet die Funktion ist", ["linksgekrümmt", "rechtsgekrümmt",
       "konstant", "fallend"], 0, "Linksgekrümmt (konvex)."),
    NUM("Extremstelle von f(x)=x²-6x+1 (f'(x)=2x-6)?", 6/2, 0.001, "", "2x-6=0 → x=3."),
  ),
  "exp-log": T("Exponential- & Logarithmusfunktionen",
    NUM("Berechne log₁₀(1000).", math.log10(1000), 0.001, "", "10³=1000 → 3."),
    MC("Ableitung von f(x) = eˣ?", ["x·eˣ⁻¹", "eˣ", "1/x", "ln(x)"], 1, "eˣ."),
    NUM("Berechne ln(1).", math.log(1), 0.001, "", "e⁰=1 → 0."),
    MC("log(a·b) =", ["log a · log b", "log a + log b", "log a - log b", "log a / log b"], 1, "Produkt → Summe."),
    NUM("Berechne log₂(8).", math.log2(8), 0.001, "", "2³=8 → 3."),
  ),
  "folgen-reihen": T("Folgen & Reihen",
    NUM("Arithmetische Folge a₁=2, d=3. a₅ = ?", 2+(5-1)*3, 0.001, "", "aₙ=a₁+(n-1)d = 2+12 = 14."),
    NUM("Geometrische Folge a₁=3, q=2. a₄ = ?", 3*2**(4-1), 0.001, "", "aₙ=a₁·q^(n-1)=3·8=24."),
    NUM("Summe 1+2+3+...+10?", sum(range(1,11)), 0.1, "", "n(n+1)/2 = 55."),
    MC("Bei einer arithmetischen Folge ist konstant", ["der Quotient q", "die Differenz d",
       "das erste Glied", "die Summe"], 1, "Konstante Differenz d."),
  ),
  "trig-funktionen": T("Trigonometrische Funktionen",
    NUM("Periode von sin(x) in Grad?", 360, 1, "°", "sin hat Periode 360°."),
    MC("Wertebereich von sin(x)?", ["[0;1]", "[-1;1]", "[-∞;∞]", "[0;∞]"], 1, "sin liegt zwischen -1 und 1."),
    NUM("Berechne sin(90°).", math.sin(math.radians(90)), 0.01, "", "= 1."),
    NUM("Berechne cos(0°).", math.cos(math.radians(0)), 0.01, "", "= 1."),
  ),
}}

mathematik["stufen"]["4"] = {"name": "HTL 4. Klasse", "themen": {
  "integralrechnung": T("Integralrechnung",
    MC("Stammfunktion von f(x) = 2x?", ["2", "x² + C", "2x² + C", "x + C"], 1, "∫2x dx = x²+C."),
    NUM("Bestimmtes Integral ∫₀² 2x dx?", 2**2 - 0**2, 0.001, "", "[x²]₀² = 4."),
    MC("∫ eˣ dx =", ["eˣ + C", "x·eˣ + C", "eˣ⁺¹ + C", "ln x + C"], 0, "eˣ+C."),
    NUM("∫₁³ 1 dx = ?", 3-1, 0.001, "", "[x]₁³ = 2."),
    NUM("∫₀³ x² dx = ? (Stammfkt. x³/3)", 3**3/3 - 0, 0.01, "", "27/3 = 9."),
  ),
  "komplexe-zahlen": T("Komplexe Zahlen",
    MC("i² =", ["1", "-1", "i", "0"], 1, "Definition i²=-1."),
    NUM("Betrag von z = 3 + 4i?", math.hypot(3,4), 0.01, "", "√(3²+4²)=5."),
    MC("Konjugiert komplexe Zahl zu 2 - 5i?", ["-2+5i", "2+5i", "-2-5i", "5-2i"], 1, "2+5i."),
    MC("Summe (1+2i)+(3+i) =", ["4+3i", "4+2i", "3+3i", "4+i"], 0, "Real- und Imaginärteil addieren: 4+3i."),
  ),
  "statistik": T("Beschreibende Statistik",
    NUM("Mittelwert von 4, 8, 10, 6, 2?", (4+8+10+6+2)/5, 0.01, "", "30/5 = 6."),
    NUM("Median von 3, 7, 2, 9, 5 (sortiert)?", sorted([3,7,2,9,5])[2], 0.01, "", "2,3,5,7,9 → 5."),
    NUM("Spannweite von 12, 4, 9, 20, 7?", 20-4, 0.01, "", "Max-Min = 20-4 = 16."),
    MC("Der Modus ist", ["der Mittelwert", "der häufigste Wert",
       "der mittlere Wert", "die Summe"], 1, "Häufigster Wert."),
  ),
  "wahrscheinlichkeit": T("Wahrscheinlichkeit",
    NUM("P(6) bei fairem Würfel (Dezimal, 3 Stellen)?", 1/6, 0.002, "", "1/6 ≈ 0,167."),
    NUM("P(zweimal Kopf) bei 2 Münzen (Dezimal)?", 0.5*0.5, 0.001, "", "0,5·0,5 = 0,25."),
    MC("Summe aller Wahrscheinlichkeiten?", ["0", "0,5", "1", "100"], 2, "Normierung = 1."),
    NUM("P(gerade Zahl) bei fairem Würfel (Dezimal)?", 3/6, 0.001, "", "{2,4,6} → 3/6 = 0,5."),
  ),
  "vektoren-3d": T("Vektoren im Raum",
    NUM("Länge des Vektors (2; 3; 6)?", math.sqrt(2**2+3**2+6**2), 0.01, "", "√(4+9+36)=√49=7."),
    NUM("Skalarprodukt (1;2;3)·(4;0;1)?", 1*4+2*0+3*1, 0.01, "", "4+0+3 = 7."),
    MC("Ein Vektor im Raum hat", ["1 Komponente", "2 Komponenten",
       "3 Komponenten", "4 Komponenten"], 2, "3 Komponenten (x,y,z)."),
  ),
}}

mathematik["stufen"]["5"] = {"name": "HTL 5. Klasse", "themen": {
  "differentialgleichungen": T("Differentialgleichungen",
    MC("Lösung von y' = y?", ["y = x²", "y = C·eˣ", "y = sin x", "y = ln x"], 1, "y = C·eˣ."),
    MC("Ordnung einer DGL = höchste vorkommende", ["Funktion", "Ableitung",
       "Konstante", "Variable"], 1, "Höchste Ableitung."),
    MC("y' = k·y beschreibt", ["lineares Wachstum", "exponentielles Wachstum",
       "konstante Funktion", "Schwingung"], 1, "Exponentielles Wachstum/Zerfall."),
  ),
  "verteilungen": T("Wahrscheinlichkeitsverteilungen",
    NUM("Erwartungswert beim Würfel (1..6)?", sum(range(1,7))/6, 0.01, "", "(1+..+6)/6 = 3,5."),
    MC("Die Binomialverteilung beschreibt", ["stetige Daten", "Anzahl Erfolge bei n Versuchen",
       "Mittelwerte", "Zeitreihen"], 1, "Erfolge bei n Bernoulli-Versuchen."),
    MC("Die Gauß-Verteilung hat die Form einer", ["Geraden", "Glockenkurve",
       "Treppe", "Parabel"], 1, "Glockenkurve."),
    NUM("Binomial: n=10, p=0,5. Erwartungswert μ = n·p?", 10*0.5, 0.01, "", "μ = n·p = 5."),
  ),
  "beurteilende-statistik": T("Beurteilende Statistik",
    MC("Ein Konfidenzintervall gibt an", ["den exakten Wert", "einen Bereich für den Parameter",
       "den Mittelwert", "die Summe"], 1, "Bereich, in dem der Parameter mit best. Sicherheit liegt."),
    MC("Ein übliches Konfidenzniveau ist", ["5 %", "50 %", "95 %", "150 %"], 2, "Häufig 95 %."),
  ),
  "matura-mix": T("Matura-Mix (gemischt)",
    NUM("Ableitung von f(x)=x² an der Stelle x=3?", 2*3, 0.001, "", "f'(x)=2x → 6."),
    NUM("∫₀¹ 2x dx?", 1**2, 0.001, "", "[x²]₀¹ = 1."),
    NUM("15 % von 240?", 240*0.15, 0.01, "", "= 36."),
    MC("sin²α + cos²α =", ["0", "1", "2", "tan α"], 1, "Trigonometrischer Pythagoras = 1."),
  ),
}}

# =====================================================================
#  PHYSIK
# =====================================================================
physik = {"name": "Physik", "stufen": {}}

physik["stufen"]["1"] = {"name": "HTL 1. Klasse", "themen": {
  "groessen-einheiten": T("Größen & Einheiten",
    MC("SI-Einheit der Länge?", ["cm", "m", "km", "mm"], 1, "Meter."),
    MC("SI-Einheit der Kraft?", ["Joule", "Newton", "Watt", "Pascal"], 1, "Newton."),
    NUM("Wandle 72 km/h in m/s um.", 72/3.6, 0.1, "m/s", "72/3,6 = 20."),
    NUM("Wandle 250 g in kg um.", 250/1000, 0.001, "kg", "= 0,25 kg."),
    MC("Die Basisgröße Zeit hat die Einheit", ["Meter", "Sekunde", "Kelvin", "Mol"], 1, "Sekunde."),
  ),
  "kinematik-gleichfoermig": T("Kinematik (gleichförmig)",
    MC("Einheit der Geschwindigkeit (SI)?", ["km/h", "m/s", "m/s²", "N"], 1, "m/s."),
    NUM("150 km in 2 h: Durchschnittsgeschwindigkeit?", 150/2, 0.1, "km/h", "v=s/t=75."),
    NUM("Mit 10 m/s: Strecke in 5 s (gleichförmig)?", 10*5, 0.1, "m", "s=v·t=50."),
    NUM("Zeit für 300 m bei 15 m/s?", 300/15, 0.1, "s", "t=s/v=20."),
  ),
  "kinematik-beschleunigt": T("Kinematik (beschleunigt)",
    NUM("Beschleunigung: von 0 auf 20 m/s in 4 s?", 20/4, 0.01, "m/s²", "a=Δv/t=5."),
    NUM("Freier Fall: Geschwindigkeit nach 3 s (g=9,81)?", 9.81*3, 0.1, "m/s", "v=g·t≈29,43."),
    NUM("Freier Fall: Fallstrecke in 2 s (s=½g t²)?", 0.5*9.81*2**2, 0.2, "m", "s=½·9,81·4≈19,62."),
    MC("Einheit der Beschleunigung?", ["m/s", "m/s²", "N", "J"], 1, "m/s²."),
  ),
  "kraefte-dichte": T("Kräfte & Dichte",
    MC("Newtonsches Grundgesetz?", ["F=m/a", "F=m·a", "F=a/m", "F=m·v"], 1, "F=m·a."),
    NUM("Gewichtskraft von 5 kg (g=9,81)?", 5*9.81, 0.5, "N", "F=m·g≈49,05."),
    NUM("Dichte von 200 g auf 250 cm³?", 200/250, 0.01, "g/cm³", "ρ=m/V=0,8."),
    NUM("Masse bei ρ=2 g/cm³ und V=50 cm³?", 2*50, 0.1, "g", "m=ρ·V=100."),
  ),
  "druck": T("Druck",
    MC("Einheit des Drucks?", ["Newton", "Pascal", "Joule", "Watt"], 1, "Pascal = N/m²."),
    NUM("Druck: 200 N auf 0,5 m²?", 200/0.5, 1, "Pa", "p=F/A=400."),
    NUM("Kraft bei p=1000 Pa auf A=2 m²?", 1000*2, 1, "N", "F=p·A=2000."),
    MC("Wie viel Pascal sind 1 bar?", ["100 Pa", "1000 Pa", "100 000 Pa", "1 Pa"], 2, "1 bar = 10⁵ Pa."),
  ),
}}

physik["stufen"]["2"] = {"name": "HTL 2. Klasse", "themen": {
  "dynamik": T("Dynamik (Newton'sche Gesetze)",
    MC("Das Trägheitsgesetz ist Newtons", ["1. Gesetz", "2. Gesetz", "3. Gesetz", "Gravitationsgesetz"], 0, "1. Newton'sches Gesetz."),
    NUM("Kraft, um 10 kg mit 3 m/s² zu beschleunigen?", 10*3, 0.1, "N", "F=m·a=30."),
    NUM("Beschleunigung: 50 N auf 10 kg?", 50/10, 0.01, "m/s²", "a=F/m=5."),
    MC("'Actio = Reactio' ist Newtons", ["1. Gesetz", "2. Gesetz", "3. Gesetz", "0. Gesetz"], 2, "3. Gesetz."),
  ),
  "energie": T("Arbeit, Energie & Leistung",
    MC("Einheit der Energie?", ["Newton", "Joule", "Watt", "Volt"], 1, "Joule."),
    NUM("Hubarbeit: 10 kg um 2 m heben (g=9,81)?", 10*9.81*2, 1, "J", "W=m·g·h≈196,2."),
    NUM("Kinetische Energie: 2 kg bei 3 m/s?", 0.5*2*3**2, 0.1, "J", "E=½mv²=9."),
    NUM("Leistung: 600 J in 3 s?", 600/3, 0.5, "W", "P=W/t=200."),
    MC("1 kW entspricht", ["100 W", "1000 W", "10 W", "1 000 000 W"], 1, "1 kW = 1000 W."),
  ),
  "impuls": T("Impuls",
    NUM("Impuls: 4 kg bei 5 m/s?", 4*5, 0.1, "kg·m/s", "p=m·v=20."),
    MC("Einheit des Impulses?", ["N", "kg·m/s", "J", "W"], 1, "kg·m/s."),
    NUM("Geschwindigkeit bei p=30 kg·m/s und m=6 kg?", 30/6, 0.01, "m/s", "v=p/m=5."),
    MC("Der Impuls bleibt erhalten in einem", ["offenen System", "abgeschlossenen System",
       "beschleunigten System", "warmen System"], 1, "Impulserhaltung im abgeschlossenen System."),
  ),
  "waermelehre": T("Wärmelehre",
    NUM("0 °C in Kelvin?", 273.15, 0.5, "K", "T(K)=T(°C)+273,15."),
    NUM("100 °C in Kelvin?", 100+273.15, 0.5, "K", "= 373,15 K."),
    MC("Wärmemenge Q =", ["m·c·ΔT", "m·g·h", "½mv²", "U·I"], 0, "Q=m·c·ΔT."),
    MC("Fest → flüssig heißt", ["Verdampfen", "Schmelzen", "Sublimieren", "Kondensieren"], 1, "Schmelzen."),
  ),
  "gase": T("Gasgesetze",
    MC("Allgemeine Gasgleichung?", ["p·V=n·R·T", "p·V=m·g·h", "p=R/T", "V=p·T"], 0, "Ideales Gas: pV=nRT."),
    MC("Bei konstanter Temperatur gilt (Boyle-Mariotte)", ["p·V = const", "p/V = const",
       "p+V = const", "p=V"], 0, "p·V konstant."),
    NUM("Verdoppelt man p bei T=const, wird V ...-fach? (Faktor)", 0.5, 0.01, "", "V halbiert sich → Faktor 0,5."),
  ),
}}

physik["stufen"]["3"] = {"name": "HTL 3. Klasse", "themen": {
  "elektrizitaet": T("Elektrizität (Gleichstrom)",
    MC("Ohmsches Gesetz?", ["U=R/I", "U=R·I", "U=I/R", "U=P·I"], 1, "U=R·I."),
    NUM("Strom bei U=12 V, R=4 Ω?", 12/4, 0.01, "A", "I=U/R=3."),
    NUM("Leistung bei U=230 V, I=2 A?", 230*2, 1, "W", "P=U·I=460."),
    NUM("Gesamtwiderstand 3 Ω + 6 Ω in Serie?", 3+6, 0.1, "Ω", "Serie: R=R₁+R₂=9."),
    NUM("Gesamtwiderstand 6 Ω ∥ 3 Ω (parallel)?", 1/(1/6+1/3), 0.05, "Ω", "1/R=1/6+1/3 → R=2."),
  ),
  "magnetismus": T("Magnetismus",
    MC("Gleichnamige Magnetpole", ["ziehen sich an", "stoßen sich ab",
       "tun nichts", "verschmelzen"], 1, "Gleichnamige Pole stoßen sich ab."),
    MC("Ein stromdurchflossener Leiter erzeugt", ["ein elektrisches Feld", "ein Magnetfeld",
       "Wärme nur", "Licht"], 1, "Magnetfeld um den Leiter."),
    MC("Einheit der magnetischen Flussdichte?", ["Tesla", "Weber", "Henry", "Gauß (SI: Tesla)"], 0, "Tesla."),
  ),
  "schwingungen": T("Schwingungen & Wellen",
    MC("Einheit der Frequenz?", ["Sekunde", "Hertz", "Meter", "Watt"], 1, "Hertz = 1/s."),
    NUM("Periodendauer bei f=50 Hz?", 1/50, 0.001, "s", "T=1/f=0,02."),
    NUM("Wellenlänge bei v=340 m/s, f=170 Hz?", 340/170, 0.05, "m", "λ=v/f=2."),
    NUM("Frequenz bei T=0,004 s?", 1/0.004, 1, "Hz", "f=1/T=250."),
  ),
  "akustik": T("Akustik",
    NUM("Schallgeschwindigkeit in Luft (ca.)?", 340, 10, "m/s", "≈ 340 m/s bei 20 °C."),
    MC("Lautstärke wird gemessen in", ["Hertz", "Dezibel", "Newton", "Watt"], 1, "Dezibel (dB)."),
    NUM("Entfernung eines Gewitters: Donner 3 s nach Blitz (v≈340 m/s)?", 340*3, 20, "m", "s=v·t≈1020 m."),
  ),
}}

physik["stufen"]["4"] = {"name": "HTL 4. Klasse", "themen": {
  "optik": T("Optik",
    MC("Reflexionsgesetz:", ["Einfallswinkel > Ausfallswinkel", "Einfallswinkel = Ausfallswinkel",
       "Einfallswinkel < Ausfallswinkel", "unabhängig"], 1, "Einfallswinkel = Reflexionswinkel."),
    MC("Übergang Luft → Glas: Licht wird", ["vom Lot weg gebrochen", "zum Lot hin gebrochen",
       "nicht gebrochen", "absorbiert"], 1, "Zum Lot hin (dichteres Medium)."),
    NUM("Lichtgeschwindigkeit im Vakuum (·10⁸ m/s, nur Zahl)?", 3, 0.05, "·10⁸ m/s", "c ≈ 3·10⁸ m/s."),
    MC("Eine Sammellinse ist in der Mitte", ["dünner", "dicker", "flach", "verspiegelt"], 1, "In der Mitte dicker (konvex)."),
  ),
  "induktion": T("Elektromagnetische Induktion",
    MC("Induktion entsteht durch", ["konstantes Magnetfeld", "Änderung des magnetischen Flusses",
       "konstanten Strom", "Reibung"], 1, "Flussänderung induziert Spannung."),
    MC("Das Prinzip nutzt ein", ["Widerstand", "Generator", "Kondensator (nur)", "Ohmmeter"], 1, "Generator wandelt Bewegung in Spannung."),
    MC("Die Lenz'sche Regel betrifft die", ["Richtung des Induktionsstroms", "Größe der Masse",
       "Lichtgeschwindigkeit", "Temperatur"], 0, "Induktionsstrom wirkt seiner Ursache entgegen."),
  ),
  "wechselstrom": T("Wechselstrom",
    NUM("Netzfrequenz in Europa?", 50, 1, "Hz", "50 Hz."),
    MC("Bei Wechselstrom ändert sich periodisch die", ["Masse", "Stromrichtung",
       "Temperatur", "Länge"], 1, "Stromrichtung wechselt periodisch."),
    NUM("Effektivwert: Scheitelspannung 325 V → U_eff = Û/√2 (gerundet)?", 325/math.sqrt(2), 2, "V", "≈ 230 V."),
  ),
  "thermodynamik": T("Thermodynamik",
    MC("1. Hauptsatz: Erhaltung der", ["Masse", "Energie", "Ladung", "Temperatur"], 1, "Energieerhaltung."),
    MC("Der Wirkungsgrad kann höchstens", ["> 1 sein", "= 1 (100 %) sein",
       "negativ sein", "unendlich sein"], 1, "η ≤ 1."),
    NUM("Wirkungsgrad: 300 J Nutzen aus 1200 J (in %)?", 300/1200*100, 0.5, "%", "η=W_nutz/W_zu=25 %."),
  ),
}}

physik["stufen"]["5"] = {"name": "HTL 5. Klasse", "themen": {
  "atomphysik": T("Atomphysik",
    MC("Der Atomkern besteht aus", ["Protonen und Elektronen", "Protonen und Neutronen",
       "nur Neutronen", "Elektronen und Neutronen"], 1, "Nukleonen = Protonen + Neutronen."),
    MC("Die Elektronen befinden sich", ["im Kern", "in der Hülle",
       "zwischen Kernen", "im Vakuum nur"], 1, "In der Atomhülle."),
    MC("Die Ladung eines Protons ist", ["negativ", "positiv", "neutral", "variabel"], 1, "Positiv."),
  ),
  "kernphysik": T("Kernphysik",
    NUM("Nach wie vielen Halbwertszeiten ist 1/8 übrig?", 3, 0.001, "", "(½)³=1/8 → 3."),
    NUM("Nach wie vielen Halbwertszeiten ist 1/4 übrig?", 2, 0.001, "", "(½)²=1/4 → 2."),
    MC("Geringste Reichweite / stärkste Ionisation hat", ["Alpha", "Beta", "Gamma", "Röntgen"], 0, "Alpha-Strahlung."),
    MC("Gamma-Strahlung ist", ["ein Heliumkern", "ein Elektron",
       "elektromagnetische Strahlung", "ein Proton"], 2, "Energiereiche EM-Strahlung."),
  ),
  "relativitaet": T("Relativität",
    MC("Einsteins Masse-Energie-Beziehung?", ["E=m·c", "E=m·c²", "E=½mc²", "E=m/c²"], 1, "E=m·c²."),
    MC("Nichts kann schneller sein als", ["der Schall", "das Licht",
       "ein Flugzeug", "ein Satellit"], 1, "Lichtgeschwindigkeit als Grenze."),
    NUM("Lichtgeschwindigkeit (·10⁸ m/s, nur Zahl)?", 3, 0.05, "·10⁸ m/s", "c≈3·10⁸ m/s."),
  ),
  "moderne-physik": T("Moderne Physik",
    MC("Licht zeigt Eigenschaften von", ["nur Wellen", "nur Teilchen",
       "Wellen und Teilchen", "nichts davon"], 2, "Welle-Teilchen-Dualismus."),
    MC("Das Photon ist ein", ["Lichtquant", "Atomkern", "Elektron", "Neutron"], 0, "Energiequant des Lichts."),
    MC("Die Quantenphysik beschreibt", ["sehr große Objekte", "sehr kleine Objekte (Atome)",
       "nur Planeten", "nur Schall"], 1, "Mikrokosmos (Atome, Teilchen)."),
  ),
}}

# =====================================================================
#  Zusammenbauen, IDs vergeben, speichern
# =====================================================================
faecher = {"mathematik": mathematik, "physik": physik}

for fk, fach in faecher.items():
    for sk, stufe in fach["stufen"].items():
        for tk, thema in stufe["themen"].items():
            for i, q in enumerate(thema["fragen"], start=1):
                q["id"] = f"{fk[0]}{sk}-{tk}-{i}"

out = {"faecher": faecher}
ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fragen.json")
with open(ziel, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# kleine Statistik
n_themen = sum(len(s["themen"]) for fa in faecher.values() for s in fa["stufen"].values())
n_fragen = sum(len(t["fragen"]) for fa in faecher.values() for s in fa["stufen"].values() for t in s["themen"].values())
print(f"Geschrieben: {ziel}")
print(f"Faecher: {len(faecher)} | Themen: {n_themen} | Fragen: {n_fragen}")
for fk, fach in faecher.items():
    for sk, stufe in fach["stufen"].items():
        print(f"  {fk} Stufe {sk}: {len(stufe['themen'])} Themen")
