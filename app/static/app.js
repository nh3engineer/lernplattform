"use strict";

let BAUM = [];
let AKTUELL = null;     // { fach, stufe, thema, modus, fragen, kontext, name, email }
let MODUS = "uebung";   // "uebung" | "pruefung"
let TIMER = null;       // Intervall-ID
let REST = 0;           // verbleibende Sekunden

const $ = (id) => document.getElementById(id);

async function init() {
  const res = await fetch("/api/faecher");
  BAUM = await res.json();
  const fachSel = $("fach");
  fachSel.innerHTML = '<option value="">-- wählen --</option>';
  BAUM.forEach(f => {
    const o = document.createElement("option");
    o.value = f.key; o.textContent = f.name;
    fachSel.appendChild(o);
  });
}

function fuelleStufen() {
  const fach = BAUM.find(f => f.key === $("fach").value);
  const stufeSel = $("stufe");
  const themaSel = $("thema");
  stufeSel.innerHTML = '<option value="">-- wählen --</option>';
  themaSel.innerHTML = '<option value="">-- zuerst Stufe wählen --</option>';
  themaSel.disabled = true;
  stufeSel.disabled = !fach;
  if (!fach) return;
  fach.stufen.forEach(s => {
    const o = document.createElement("option");
    o.value = s.key; o.textContent = s.name;
    stufeSel.appendChild(o);
  });
}

function fuelleThemen() {
  const fach = BAUM.find(f => f.key === $("fach").value);
  const stufe = fach ? fach.stufen.find(s => s.key === $("stufe").value) : null;
  const themaSel = $("thema");
  themaSel.innerHTML = '<option value="">-- wählen --</option>';
  themaSel.disabled = !stufe;
  if (!stufe) return;
  // Option: ganze Schulstufe (alle Themen)
  const oAlle = document.createElement("option");
  oAlle.value = "__alle__";
  oAlle.textContent = `Alle Themen der Schulstufe (${stufe.gesamt} Fragen)`;
  themaSel.appendChild(oAlle);
  stufe.themen.forEach(t => {
    const o = document.createElement("option");
    o.value = t.key;
    o.textContent = `${t.name} (${t.anzahl} Fragen)`;
    themaSel.appendChild(o);
  });
}

function setzeModus(m) {
  MODUS = m;
  const uebung = m === "uebung";
  $("modus-uebung").classList.toggle("aktiv", uebung);
  $("modus-uebung").setAttribute("aria-pressed", String(uebung));
  $("modus-pruefung").classList.toggle("aktiv", !uebung);
  $("modus-pruefung").setAttribute("aria-pressed", String(!uebung));
  $("pruefung-felder").classList.toggle("versteckt", uebung);
  $("btn-start").textContent = uebung ? "Übung starten" : "Prüfung starten";
  // Prüfung: Standardmäßig "Alle Themen" vorschlagen, falls vorhanden
  if (!uebung) {
    const themaSel = $("thema");
    if (!themaSel.disabled && themaSel.value === "" && themaSel.options.length > 1) {
      themaSel.value = "__alle__";
    }
  }
}

async function starten() {
  const fach = $("fach").value, stufe = $("stufe").value, thema = $("thema").value;
  if (!fach || !stufe || !thema) {
    melden("auswahl-msg", "Bitte Fach, Schulstufe und Themengebiet wählen.", "err");
    return;
  }
  let name = "", email = "";
  if (MODUS === "pruefung") {
    name = $("name").value.trim();
    email = $("email").value.trim();
    if (!email || !email.includes("@")) {
      melden("auswahl-msg", "Für eine Prüfung bitte zuerst eine gültige E-Mail-Adresse eingeben.", "err");
      return;
    }
  }

  const url = `/api/pruefung?fach=${fach}&stufe=${stufe}&thema=${encodeURIComponent(thema)}&modus=${MODUS}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.fehler) { melden("auswahl-msg", data.fehler, "err"); return; }

  AKTUELL = {
    fach, stufe, thema, modus: MODUS, name, email,
    fragen: data.fragen,
    kontext: { fach_name: data.fach_name, stufe_name: data.stufe_name, thema_name: data.thema_name },
  };

  $("pruefung-titel").textContent =
    `${data.fach_name} · ${data.stufe_name} · ${data.thema_name}`;
  $("btn-abgeben").textContent = (MODUS === "uebung") ? "Lösungen anzeigen" : "Prüfung abgeben";
  rendereFragen(data.fragen);

  // Timer nur bei Pruefung
  stoppeTimer();
  if (MODUS === "pruefung" && data.dauer_min) {
    starteTimer(data.dauer_min * 60);
    $("timer-bar").classList.remove("versteckt");
  } else {
    $("timer-bar").classList.add("versteckt");
  }

  melden("auswahl-msg", "", "");
  melden("abgabe-msg", "", "");
  $("bereich-auswahl").classList.add("versteckt");
  $("bereich-pruefung").classList.remove("versteckt");
  $("bereich-ergebnis").classList.add("versteckt");
  window.scrollTo(0, 0);
}

function starteTimer(sekunden) {
  REST = sekunden;
  aktualisiereTimer();
  TIMER = setInterval(() => {
    REST -= 1;
    aktualisiereTimer();
    if (REST <= 0) {
      stoppeTimer();
      melden("abgabe-msg", "Zeit abgelaufen – die Prüfung wurde automatisch abgegeben.", "err");
      abgeben(true);
    }
  }, 1000);
}
function stoppeTimer() {
  if (TIMER) { clearInterval(TIMER); TIMER = null; }
}
function aktualisiereTimer() {
  const m = Math.floor(Math.max(0, REST) / 60);
  const s = Math.max(0, REST) % 60;
  const el = $("timer-zeit");
  el.textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  el.classList.toggle("knapp", REST <= 60);
}

function rendereFragen(fragen) {
  const c = $("fragen-container");
  c.innerHTML = "";
  fragen.forEach((q, i) => {
    const div = document.createElement("div");
    div.className = "frage";
    let inner = `<div class="nr">Frage ${i + 1}</div><div class="text">${esc(q.frage)}</div>`;
    if (q.typ === "mc") {
      inner += '<div class="optionen">';
      q.optionen.forEach(opt => {
        inner += `<label><input type="radio" name="${q.id}" value="${opt.idx}"> ${esc(opt.text)}</label>`;
      });
      inner += "</div>";
    } else {
      const einheit = q.einheit ? `<span class="einheit">${esc(q.einheit)}</span>` : "";
      inner += `<div class="num-wrap"><input type="text" inputmode="decimal" name="${q.id}" placeholder="Antwort eingeben">${einheit}</div>`;
    }
    div.innerHTML = inner;
    c.appendChild(div);
  });
}

function sammleAntworten() {
  const antworten = {};
  AKTUELL.fragen.forEach(q => {
    if (q.typ === "mc") {
      const sel = document.querySelector(`input[name="${q.id}"]:checked`);
      antworten[q.id] = sel ? sel.value : null;
    } else {
      const inp = document.querySelector(`input[name="${q.id}"]`);
      antworten[q.id] = inp ? inp.value : "";
    }
  });
  return antworten;
}

async function abgeben(autoAbgabe) {
  stoppeTimer();
  const btn = $("btn-abgeben");
  btn.disabled = true;
  btn.textContent = "Wird ausgewertet …";

  const payload = {
    modus: AKTUELL.modus,
    fach_name: AKTUELL.kontext.fach_name,
    stufe_name: AKTUELL.kontext.stufe_name,
    thema_name: AKTUELL.kontext.thema_name,
    name: AKTUELL.name,
    email: AKTUELL.email,
    antworten: sammleAntworten(),
  };
  AKTUELL.letzteAbgabe = payload;

  try {
    const res = await fetch("/api/abgabe", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.fehler) { melden("abgabe-msg", data.fehler, "err"); return; }
    zeigeErgebnis(data);
  } catch (e) {
    melden("abgabe-msg", "Fehler bei der Übermittlung: " + e, "err");
  } finally {
    btn.disabled = false;
    btn.textContent = (AKTUELL.modus === "uebung") ? "Lösungen anzeigen" : "Prüfung abgeben";
  }
}

function zeigeErgebnis(data) {
  const uebung = data.modus === "uebung";
  $("ergebnis-titel").textContent = uebung ? "Übungs-Auswertung" : "Prüfungs-Auswertung";
  $("detail-ueberschrift").textContent = uebung ? "Lösungen" : "Detailauswertung";
  $("stat-punkte").textContent = `${data.punkte} / ${data.max_punkte}`;
  $("stat-prozent").textContent = `${data.prozent} %`;
  $("stat-note").textContent = data.note;

  const dc = $("detail-container");
  dc.innerHTML = "";
  data.details.forEach((d, i) => {
    const div = document.createElement("div");
    div.className = "detail " + (d.richtig ? "ok" : "no");
    div.innerHTML =
      `<div class="mark">${d.richtig ? "✓" : "✗"}</div>
       <div>
         <div><b>${i + 1}. ${esc(d.frage)}</b></div>
         <div class="meta">Deine Antwort: ${esc(d.deine_antwort)}</div>
         <div class="meta">Richtige Antwort: <b>${esc(d.loesung)}</b></div>
         <div class="meta"><i>${esc(d.erklaerung)}</i></div>
       </div>`;
    dc.appendChild(div);
  });

  const mailEl = $("mail-status");
  const pdfBtn = $("btn-pdf");
  if (uebung) {
    mailEl.classList.add("versteckt");
    pdfBtn.classList.add("versteckt");
  } else {
    // Mail-Status anzeigen
    let mtext = "", mtyp = "ok";
    const m = data.mail || {};
    if (m.versendet && m.versendet.length) {
      mtext = "PDF versendet an: " + m.versendet.join(", ");
    }
    if (m.gespeichert) {
      mtext += (mtext ? " – " : "") +
        "Hinweis: E-Mail-Versand ist nicht konfiguriert, das PDF wurde lokal gespeichert.";
      mtyp = "err";
    }
    mailEl.textContent = mtext || "Auswertung abgeschlossen.";
    mailEl.className = "msg " + mtyp;
    mailEl.classList.remove("versteckt");
    pdfBtn.classList.remove("versteckt");
  }

  $("timer-bar").classList.add("versteckt");
  $("bereich-pruefung").classList.add("versteckt");
  $("bereich-ergebnis").classList.remove("versteckt");
  window.scrollTo(0, 0);
}

async function pdfDownload() {
  if (!AKTUELL || !AKTUELL.letzteAbgabe) return;
  const res = await fetch("/api/pdf", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(AKTUELL.letzteAbgabe),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "auswertung.pdf"; a.click();
  URL.revokeObjectURL(url);
}

function abbrechen() {
  stoppeTimer();
  $("timer-bar").classList.add("versteckt");
  $("bereich-pruefung").classList.add("versteckt");
  $("bereich-auswahl").classList.remove("versteckt");
}

function neuStarten() {
  $("bereich-ergebnis").classList.add("versteckt");
  $("bereich-auswahl").classList.remove("versteckt");
  melden("auswahl-msg", "", "");
  melden("abgabe-msg", "", "");
}

function melden(id, text, typ) {
  const el = $(id);
  el.textContent = text;
  el.className = text ? "msg " + typ : "msg versteckt";
}
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

document.addEventListener("DOMContentLoaded", () => {
  init();
  $("fach").addEventListener("change", fuelleStufen);
  $("stufe").addEventListener("change", fuelleThemen);
  $("modus-uebung").addEventListener("click", () => setzeModus("uebung"));
  $("modus-pruefung").addEventListener("click", () => setzeModus("pruefung"));
  $("btn-start").addEventListener("click", starten);
  $("btn-abgeben").addEventListener("click", () => abgeben(false));
  $("btn-abbrechen").addEventListener("click", abbrechen);
  $("btn-pdf").addEventListener("click", pdfDownload);
  $("btn-neu").addEventListener("click", neuStarten);
});
