"""Aggiorna SOLO l'ultimo indice pubblicato dalla pagina ufficiale ISTAT; fallisce senza sovrascrivere in caso di parsing incerto."""
import json,re,datetime,urllib.request,pathlib,html
url='https://www.istat.it/Notizia/Indice-Dei-Prezzi-Per-Le-Rivalutazioni-Monetarie/'
p=pathlib.Path(__file__).resolve().parents[1]/'calcolatori/dati/istat-foi.json'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; FOI-Update/1.0)'})
with urllib.request.urlopen(req,timeout=25) as response: raw=response.read().decode('utf-8','replace')
txt=re.sub(r'<[^>]*>',' ',raw);txt=html.unescape(txt);txt=re.sub(r'\s+',' ',txt)
months={'GENNAIO':1,'FEBBRAIO':2,'MARZO':3,'APRILE':4,'MAGGIO':5,'GIUGNO':6,'LUGLIO':7,'AGOSTO':8,'SETTEMBRE':9,'OTTOBRE':10,'NOVEMBRE':11,'DICEMBRE':12}
m=re.search(r'Periodo di riferimento\s*:\s*('+ '|'.join(months)+r')\s+(20\d{2})',txt,re.I)
v=re.search(r'Indice generale FOI\s*\(base di riferimento\s*(20\d{2})\s*=\s*100\)[^0-9]{0,40}(\d{2,3}[,.]\d)',txt,re.I)
if not (m and v):raise SystemExit('Formato ISTAT non riconosciuto: nessuna modifica ai dati')
period=f'{int(m.group(2)):04d}-{months[m.group(1).upper()]:02d}'
value=float(v.group(2).replace(',','.'));base=int(v.group(1))
if not (90<=value<=200 and 2015<=base<=2035):raise SystemExit('Valori fuori intervallo atteso')
data=json.loads(p.read_text()); existing=data['months'].get(period)
if existing and (existing['value']!=value or existing['base']!=base):raise SystemExit('Indice già presente ma differente: revisione manuale necessaria')
data['months'][period]={'value':value,'base':base}
data['latest']=max(data['months']);data['checked_at']=datetime.date.today().isoformat();data['source']=url
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Aggiornato',period,value)
