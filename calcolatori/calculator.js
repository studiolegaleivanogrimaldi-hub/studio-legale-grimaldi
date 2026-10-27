"use strict";
const euro = n => new Intl.NumberFormat('it-IT',{style:'currency',currency:'EUR'}).format(n);
const el = id => document.getElementById(id);
function populateYears(){
 const select=el('year');
 Object.keys(window.PARAMETRI_ANNUALI||{}).sort().reverse().forEach(year=>{
  const option=document.createElement('option');option.value=year;option.textContent=year;select.appendChild(option);
 });
 if(!select.options.length){el('status').textContent='Nessun anno verificato: calcolo disabilitato.';el('calculate').disabled=true;return;}
 select.value=window.PARAMETRI_ANNUALI['2026']?'2026':select.options[0].value;
 select.addEventListener('change',showParameters);showParameters();
}
function showParameters(){
 const p=window.PARAMETRI_ANNUALI[el('year').value];
 if(!p){el('calculate').disabled=true;el('status').textContent='Parametri non verificati.';return;}
 el('calculate').disabled=false;
 el('status').textContent=`Anno ${el('year').value} · Parametri verificati il ${p.verificatoIl} · Assegno sociale ${euro(p.assegnoSociale)} · Minimo pensione ${euro(Math.max(p.minimoPensione,2*p.assegnoSociale))}. Per anni successivi occorre una nuova verifica.`;
 el('output').hidden=true;
}
function calc(){
 const p=window.PARAMETRI_ANNUALI[el('year').value];if(!p)return;
 const raw=el('income').value;
 if(raw.trim()===''||!Number.isFinite(Number(raw))||Number(raw)<0){el('output').hidden=false;el('output').textContent='Inserisci un importo netto valido e non negativo.';return;}
 const income=Number(raw),kind=document.body.dataset.kind,credit=el('credit').value,other=el('other').value;
 const protectedAmount=Math.max(p.minimoPensione,2*p.assegnoSociale);
 const base=kind==='pensione'?Math.max(0,income-protectedAmount):income;
 let rate=p.quotaOrdinaria;
 if(kind==='stipendio'&&credit==='ader')rate=income<=p.sogliaAdER1?p.quotaAdER1:income<=p.sogliaAdER2?p.quotaAdER2:p.quotaAdER3;
 const amount=base*rate;
 const out=el('output');out.replaceChildren();
 const heading=document.createElement('strong');heading.textContent='Quota teorica mensile pignorabile: '+euro(amount);out.append(heading);
 const lines=[`Somma residua teorica: ${euro(income-amount)}`,`Base di calcolo: ${euro(base)} · Aliquota: ${(rate*100).toLocaleString('it-IT',{maximumFractionDigits:2})}%`,`Anno normativo: ${el('year').value}`];
 if(kind==='pensione')lines.push(`Quota pensione protetta: ${euro(protectedAmount)}`);
 if(other==='yes')lines.push('ATTENZIONE: altri pignoramenti, cessioni o crediti alimentari richiedono un calcolo individuale.');
 lines.push('Il risultato non riguarda il pignoramento del conto corrente né costituisce parere legale.');
 lines.forEach(t=>{const x=document.createElement('p');x.textContent=t;out.append(x)});out.hidden=false;
}
document.addEventListener('DOMContentLoaded',()=>{populateYears();el('calculate').addEventListener('click',calc);el('print').addEventListener('click',()=>window.print());});
