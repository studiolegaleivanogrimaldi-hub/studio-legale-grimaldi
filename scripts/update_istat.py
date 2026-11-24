
"""Aggiornamento automatico degli indici ISTAT FOI.
Mantiene il controllo di sicurezza in caso di discordanza.
"""

import json
import re
import datetime
import urllib.request
import pathlib
import html

url = (
    "https://www.istat.it/Notizia/"
    "Indice-Dei-Prezzi-Per-Le-Rivalutazioni-Monetarie/"
)

p = (
    pathlib.Path(__file__).resolve().parents[1]
    / "calcolatori/dati/istat-foi.json"
)

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (compatible; FOI-Update/2.0)"
    }
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8", "replace")
except Exception as e:
    raise SystemExit(f"Errore collegamento ISTAT: {e}")

txt = re.sub(r"<[^>]*>", " ", raw)
txt = html.unescape(txt)
txt = re.sub(r"\s+", " ", txt)

months = {
    "GENNAIO": 1,
    "FEBBRAIO": 2,
    "MARZO": 3,
    "APRILE": 4,
    "MAGGIO": 5,
    "GIUGNO": 6,
    "LUGLIO": 7,
    "AGOSTO": 8,
    "SETTEMBRE": 9,
    "OTTOBRE": 10,
    "NOVEMBRE": 11,
    "DICEMBRE": 12
}

m = re.search(
    r"Periodo di riferimento\s*:\s*("
    + "|".join(months)
    + r")\s+(20\d{2})",
    txt,
    re.I
)

if not m:
    raise SystemExit(
        "Periodo ISTAT non riconosciuto: nessuna modifica"
    )

# Cerca l'indice dopo il periodo di riferimento.
# Non oltrepassa un eventuale periodo successivo.

section = txt[m.end():]

section = re.split(
    r"Periodo di riferimento\s*:",
    section,
    maxsplit=1,
    flags=re.I
)[0]

v = re.search(
    r"Indice generale FOI\s*"
    r"\(base di riferimento\s*(20\d{2})\s*=\s*100\)"
    r"[^0-9]{0,40}(\d{2,3}[,.]\d)(?!\d)",
    section,
    re.I
)

if not v:
    raise SystemExit(
        "Indice FOI non riconosciuto: nessuna modifica"
    )

period = (
    f"{int(m.group(2)):04d}-"
    f"{months[m.group(1).upper()]:02d}"
)

value = float(v.group(2).replace(",", "."))
base = int(v.group(1))

print("----- DATI ACQUISITI DA ISTAT -----")
print(f"Periodo: {period}")
print(f"Indice FOI: {value}")
print(f"Base di riferimento: {base}")
print(f"Fonte: {url}")

if not (90 <= value <= 200 and 2015 <= base <= 2035):
    raise SystemExit(
        "Valori fuori intervallo atteso: nessuna modifica"
    )

try:
    data = json.loads(p.read_text(encoding="utf-8"))
except Exception as e:
    raise SystemExit(f"Errore lettura archivio JSON: {e}")

existing = data["months"].get(period)

if existing is not None:

    old_value = float(existing["value"])
    old_base = int(existing["base"])

    print("----- DATI PRESENTI IN ARCHIVIO -----")
    print(f"Periodo: {period}")
    print(f"Indice archiviato: {old_value}")
    print(f"Base archiviata: {old_base}")

    if abs(old_value - value) > 0.000001 or old_base != base:

        print("----- DISCORDANZA RILEVATA -----")
        print(f"Periodo interessato: {period}")
        print(f"Indice archiviato: {old_value}")
        print(f"Nuovo indice ISTAT: {value}")
        print(f"Base archiviata: {old_base}")
        print(f"Nuova base ISTAT: {base}")
        print("Archivio mantenuto invariato.")

        raise SystemExit(
            "Revisione manuale necessaria: "
            "nessun indice sovrascritto"
        )

    print("Indice gia presente e correttamente registrato.")

else:

    data["months"][period] = {
        "value": value,
        "base": base
    }

    print(f"Nuovo indice inserito: {period} - {value}")

data["latest"] = max(data["months"])
data["checked_at"] = datetime.date.today().isoformat()
data["source"] = url

# Scrittura protetta tramite file temporaneo.

temp = p.with_suffix(".json.tmp")

temp.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ) + "\n",
    encoding="utf-8"
)

temp.replace(p)

print("----- AGGIORNAMENTO COMPLETATO -----")
print(f"Ultimo periodo disponibile: {data['latest']}")
print(f"Data verifica: {data['checked_at']}")
