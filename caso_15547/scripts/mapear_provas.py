# -*- coding: utf-8 -*-
"""mapear_provas.py - Mapeia provas do caso 15547"""
import os, sys, json, csv, subprocess
from datetime import datetime

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
BASE = r"C:\ACERVO\caso_15547"
DIR_MAP = os.path.join(BASE, "mapas")
os.makedirs(DIR_MAP, exist_ok=True)

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def count(q):
    try:
        r = subprocess.run([ES,"-instance",INST,"-get-result-count",q],
                          capture_output=True,text=True,timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except: return 0

def size(q):
    try:
        r = subprocess.run([ES,"-instance",INST,"-get-total-size",q],
                          capture_output=True,text=True,timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except: return 0

PROCESSOS = ["15547","3719","20203","10153","10153-A","23142"]
TIPOS = {
    "peticao":"ext:pdf peticao","sentenca":"ext:pdf sentenca",
    "acordao":"ext:pdf acordao","contrato":"ext:pdf contrato",
    "aditamento":"ext:pdf aditamento","fatura":"ext:pdf fatura",
    "email":"ext:eml OR ext:msg OR ext:txt email",
    "whatsapp":"ext:odt whatsapp OR ext:txt whatsapp",
    "captura":"ext:jpg captura OR ext:png captura",
    "e_redes":"E-REDES OR EREDES OR e-redes",
}
ENTIDADES = {
    "maria":"Maria Teresa","nuno":"Nuno Duarte",
    "lea":"Lisbon Experience","filipe":"Filipe Delgado",
    "joao":"Joao Cerqueira","ingo":"Ingo Schallig",
    "unicre":"Unicre","centenario":"Centenario",
}
UNIDADES = {
    "31-4":'regex:"31[-_. ]?4"',"31-5":'regex:"31[-_. ]?5"',
    "31-1":'regex:"31[-_. ]?1"',"33-2":'regex:"33[-_. ]?2"',
    "20-3":'regex:"20[-_. ]?3"',
}

def mapear():
    r = {"data":datetime.now().isoformat(),"por_processo":{},
         "por_tipo":{},"por_entidade":{},"por_unidade":{}}
    print("="*78); print("  MAPEAMENTO DE PROVAS"); print("="*78); print()
    print("[1/4] Processos...")
    for p in PROCESSOS:
        n=count(p); b=size(p); r["por_processo"][p]={"n":n,"b":b,"h":humano(b)}
        print(f"  {p:>10} {n:>8} {humano(b):>12}")
    print(); print("[2/4] Tipos...")
    for t,q in TIPOS.items():
        n=count(q); b=size(q); r["por_tipo"][t]={"n":n,"b":b,"h":humano(b),"q":q}
        print(f"  {t:<12} {n:>8} {humano(b):>12}")
    print(); print("[3/4] Entidades...")
    for e,q in ENTIDADES.items():
        n=count(q); b=size(q); r["por_entidade"][e]={"n":n,"b":b,"h":humano(b),"q":q}
        print(f"  {e:<12} {n:>8} {humano(b):>12}")
    print(); print("[4/4] Unidades...")
    for u,q in UNIDADES.items():
        n=count(q); b=size(q); r["por_unidade"][u]={"n":n,"b":b,"h":humano(b),"q":q}
        print(f"  {u:<12} {n:>8} {humano(b):>12}")
    return r

def gravar(r):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jp = os.path.join(DIR_MAP,f"mapa_provas_{ts}.json")
    cp = os.path.join(DIR_MAP,f"mapa_provas_{ts}.csv")
    with open(jp,"w",encoding="utf-8") as f:
        json.dump(r,f,indent=2,ensure_ascii=False)
    with open(cp,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["cat","chave","n","bytes","h","query"])
        for cat in ["por_processo","por_tipo","por_entidade","por_unidade"]:
            for k,v in r[cat].items():
                w.writerow([cat,k,v["n"],v["b"],v["h"],v.get("q",k)])
    print(); print(f"[OK] {jp}"); print(f"[OK] {cp}")

if __name__ == "__main__":
    gravar(mapear())
    print(); print("="*78); print("  CONCLUIDO"); print("="*78)
