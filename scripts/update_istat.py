
"""Aggiornamento automatico ISTAT FOI dalla tabella ufficiale."""

import json
import re
import datetime
import urllib.request
import pathlib
import html

url = "https://www.istat.it/Notizia/Indice-Dei-Prezzi-Per-Le-Rivalutazioni-Monetarie/"

p = (
    pathlib.Path(__file__).resolve().parents[1]
    / "calcolatori/dati/istat-foi.json"
)

req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=30) as response:
    raw = response.read().decode("utf-8", "replace")

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

pattern = (
    r"Periodo di riferimento\s*:\s*("
    + "|".join(months)
    + r")\s+(20\d{2})"
    r"\s*\(\s*aggiornamento mensile\s*\)"
    r"\s*Indice generale FOI\s*"
    r"\(base di riferimento\s*(20\d{2})\s*=\s*100\)"
    r"[^0-9]{0,40}(\d{2,3}[,.]\d)(?!\d)"
)

matches = list(re.finditer(pattern, txt, re.I))

if len(matches) != 1:
    raise SystemExit(
        "Tabella ISTAT non identificata univocamente: "
        "nessuna modifica"
    )

m = matches[0]

period = (
    f"{int(m.group(2)):04d}-"
    f"{months[m.group(1).upper()]:02d}"
)

base = int(m.group(3))
value = float(m.group(4).replace(",", "."))

print("DATI UFFICIALI ISTAT")
print(f"Periodo: {period}")
print(f"Indice FOI: {value}")
print(f"Base: {base}")

if not (90 <= value <= 200 and 2015 <= base <= 2035):
    raise SystemExit("Valori fuori intervallo atteso")

data = json.loads(p.read_text(encoding="utf-8"))

existing = data["months"].get(period)

if existing is not None:
    old_value = float(existing["value"])
    old_base = int(existing["base"])

    if abs(old_value - value) > 0.000001 or old_base != base:
        print(f"Periodo: {period}")
        print(f"Indice archiviato: {old_value}")
        print(f"Base archiviata: {old_base}")
        print(f"Indice ISTAT: {value}")
        print(f"Base ISTAT: {base}")
        raise SystemExit(
            "Discordanza: revisione manuale necessaria. "
            "Archivio invariato."
        )

    print("Indice gia presente e corretto.")

else:
    data["months"][period] = {
        "value": value,
        "base": base
    }
    print(f"Nuovo indice inserito: {period}")

data["latest"] = max(data["months"])
data["checked_at"] = datetime.date.today().isoformat()
data["source"] = url

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

print("AGGIORNAMENTO COMPLETATO")
print(f"Ultimo periodo: {data['latest']}")
print(f"Data verifica: {data['checked_at']}")
