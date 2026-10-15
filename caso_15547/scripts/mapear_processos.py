# -*- coding: utf-8 -*-
"""mapear_processos.py - Mapeia os 6 processos do caso"""
import os, sys, json, subprocess, argparse
from datetime import datetime

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
BASE = r"C:\ACERVO\caso_15547"
DIR_MAP = os.path.join(BASE, "mapas")
os.makedirs(DIR_MAP, exist_ok=True)

PROCESSOS = {
 "15547": {"nome":"15547-26.0T8LSB","tipo":"principal","acao":"Reivindicacao",
   "tribunal":"Lisboa","autora":"Maria Teresa","reu":"Nuno Duarte",
   "estado":"Em curso","relacao":"Processo principal",
   "docs":["Peticao pp.1-10","Doc.3 aditamento 05/04/2024","Doc.4 divida 105.633,75","Doc.5 contrato 31-1","Doc.6 contrato Ingo","Docs.7-8 faturas","Doc.9 E-REDES"]},
 "3719": {"nome":"3719-25.0T8LSB","tipo":"conexo","acao":"Cautelar",
   "tribunal":"Lisboa","autora":"Maria Teresa","reu":"Nuno Duarte",
   "estado":"Improcedente 27/01/2026; confirmada 16/04/2026",
   "relacao":"Decisao cautelar que antecipa factos",
   "docs":["Sentenca 27/01/2026 pp.293-302","Acordao 16/04/2026 pp.442-468","Residencia desde 2021 (indiciado)","Surpresa junho 2024 (NAO indiciado)"]},
 "20203": {"nome":"20203-22.6T8LSB","tipo":"conexo","acao":"Comercial",
   "tribunal":"Lisboa","autor":"Unicre","reu":"Nuno Duarte",
   "estado":"Condenacao 19/01/2024 (3.205,77 EUR)",
   "relacao":"Nao prova ocupacao do 31-4",
   "docs":["Peticao","Sentenca 19/01/2024 pp.1-12"]},
 "10153": {"nome":"10153-24.7T8LSB","tipo":"execucao","acao":"Execucao",
   "tribunal":"Lisboa","exequente":"Unicre","executado":"Nuno Duarte",
   "estado":"Embargos admitidos 23/10/2025",
   "relacao":"Estado provisorio",
   "docs":["Requerimento pp.1-3","Despacho admissao pp.138-139"]},
 "10153-A": {"nome":"10153-24.7T8LSB-A","tipo":"execucao","acao":"Embargos",
   "tribunal":"Lisboa","exequente":"Unicre","executado":"Nuno Duarte",
   "estado":"Em curso","relacao":"Estado provisorio",
   "docs":["Requerimento embargos","Resposta","Notificacoes"]},
 "23142": {"nome":"23142-22.7T8LSB","tipo":"execucao","acao":"Execucao",
   "tribunal":"Lisboa","exequente":"Centenario Rent","executado":"Nuno Duarte",
   "estado":"Improcedente 19/03/2026 (maioria)",
   "relacao":"Execucao distinta",
   "docs":["Requerimento","Acordao 19/03/2026 pp.13-17"]},
}

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:.2f} {u}"
        b/=1024
    return f"{b:.2f} PB"

def count(q):
    try:
        r=subprocess.run([ES,"-instance",INST,"-get-result-count",q],
                        capture_output=True,text=True,timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except: return 0

def size(q):
    try:
        r=subprocess.run([ES,"-instance",INST,"-get-total-size",q],
                        capture_output=True,text=True,timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except: return 0

def mapear():
    r={"data":datetime.now().isoformat(),"processos":{}}
    print("="*78); print("  MAPEAMENTO DE PROCESSOS"); print("="*78)
    for pid,info in PROCESSOS.items():
        n=count(pid); b=size(pid)
        info2=dict(info); info2["n"]=n; info2["b"]=b; info2["h"]=humano(b)
        r["processos"][pid]=info2
        print(); print("-"*78)
        print(f"  {pid}  |  {info['nome']}  |  {info['tipo'].upper()}")
        print("-"*78)
        print(f"  Acao:     {info['acao']}")
        print(f"  Estado:   {info['estado']}")
        print(f"  Relacao:  {info['relacao']}")
        print(f"  Ficheiros: {n}")
        print(f"  Tamanho:   {humano(b)}")
    return r

def gravar(r):
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    p=os.path.join(DIR_MAP,f"mapa_processos_{ts}.json")
    with open(p,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,ensure_ascii=False)
    print(); print(f"[OK] {p}"); return p

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--processo")
    a=p.parse_args()
    if a.processo:
        if a.processo in PROCESSOS:
            print(json.dumps(PROCESSOS[a.processo],indent=2,ensure_ascii=False))
        else: print(f"[ERRO] {a.processo}")
        return
    r=mapear(); gravar(r)
    print(); print("="*78); print("  RESUMO"); print("="*78); print()
    print(f"  {'ID':<10} {'TIPO':<10} {'FICH':>8} {'TAM':>10}  ACAO")
    print("  "+"-"*74)
    for pid,i in r["processos"].items():
        print(f"  {pid:<10} {i['tipo']:<10} {i['n']:>8} {i['h']:>10}  {i['acao']}")

if __name__ == "__main__": main()
