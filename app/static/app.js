"use strict";

let BAUM = [];
let AKTUELL = null;   // { fach, stufe, thema, fragen: [...] }

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
  stufe.themen.forEach(t => {
    const o = document.createElement("option");
    o.value = t.key;
    o.textContent = `${t.name} (${t.anzahl} Fragen)`;
    themaSel.appendChild(o);
  });
}

async function starten() {
  const fach = $("fach").value, stufe = $("stufe").value, thema = $("thema").value;
  if (!fach || !stufe || !thema) {
    melden("auswahl-msg", "Bitte Fach, Schulstufe und Themengebiet wählen.", "err");
    return;
  }
  const url = `/api/pruefung?fach=${fach}&stufe=${stufe}&thema=${thema}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.fehler) { melden("auswahl-msg", data.fehler, "err"); return; }

  AKTUELL = { fach, stufe, thema, fragen: data.fragen };
  $("pruefung-titel").textContent =
    `${data.fach_name} · ${data.stufe_name} · ${data.thema_name}`;
  rendereFragen(data.fragen);
  $("bereich-auswahl").classList.add("versteckt");
  $("bereich-pruefung").classList.remove("versteckt");
  $("bereich-ergebnis").classList.add("versteckt");
  window.scrollTo(0, 0);
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

async function abgeben() {
  const name = $("name").value.trim();
  const email = $("email").value.trim();
  if (!email || !email.includes("@")) {
    melden("abgabe-msg", "Bitte eine gültige E-Mail-Adresse eingeben – dorthin wird das PDF geschickt.", "err");
    return;
  }
  const btn = $("btn-abgeben");
  btn.disabled = true; btn.textContent = "Wird ausgewertet …";

  const payload = {
    fach: AKTUELL.fach, stufe: AKTUELL.stufe, thema: AKTUELL.thema,
    name, email, antworten: sammleAntworten(),
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
    btn.disabled = false; btn.textContent = "Prüfung abgeben & auswerten";
  }
}

function zeigeErgebnis(data) {
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
         <div class="meta">Richtige Antwort: ${esc(d.loesung)}</div>
         <div class="meta"><i>${esc(d.erklaerung)}</i></div>
       </div>`;
    dc.appendChild(div);
  });

  // Mail-Status
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
  if (m.fehler && m.fehler.length && !m.versendet.length) {
    mtyp = "err";
  }
  $("mail-status").textContent = mtext || "Auswertung abgeschlossen.";
  $("mail-status").className = "msg " + mtyp;

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
  $("btn-start").addEventListener("click", starten);
  $("btn-abgeben").addEventListener("click", abgeben);
  $("btn-pdf").addEventListener("click", pdfDownload);
  $("btn-neu").addEventListener("click", neuStarten);
});
