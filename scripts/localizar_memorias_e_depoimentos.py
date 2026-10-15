import urllib.request
import urllib.parse
import json
from pathlib import Path

def query_everything(q, max_count=50):
    url = "http://127.0.0.1:8080/?search=" + urllib.parse.quote(q) + f"&json=1&count={max_count}&path_column=1&size_column=1&date_modified_column=1"
    try:
        req = urllib.request.urlopen(url, timeout=10)
        return json.loads(req.read().decode("utf-8"))
    except Exception as e:
        print(f"Erro ao consultar {q}: {e}")
        return {}

def main():
    print("--- 1. PESQUISA DE FOTOS DE FAMÍLIA, CÃES, GATOS, PESSOAL ---")
    family_queries = [
        "ext:jpg;jpeg;png;heic;mp4;mov sobrinha",
        "ext:jpg;jpeg;png;heic;mp4;mov sobrinho",
        "ext:jpg;jpeg;png;heic;mp4;mov cão OR cao OR caes OR cães",
        "ext:jpg;jpeg;png;heic;mp4;mov gato OR gatos",
        "ext:jpg;jpeg;png;heic;mp4;mov mae OR mãe OR familia OR família",
        "path:Pessoal ext:jpg;jpeg;png;heic;mp4;mov",
        "path:Google Photos ext:jpg;jpeg;png;heic",
        "path:Takeout ext:jpg;jpeg;png;heic"
    ]
    
    for q in family_queries:
        res = query_everything(q, 10)
        total = res.get("totalResults", len(res.get("results", [])))
        print(f"[FOTOS] '{q}' -> Total: {total}")
        for r in res.get("results", [])[:3]:
            p = r.get("path", "") + "\\" + r.get("name", "")
            print(f"   -> {p}")

    print("\n--- 2. PESQUISA DE TRANSCRIÇÕES, ATAS E DEPOIMENTOS EM TRIBUNAL (3719 E 15547) ---")
    court_queries = [
        "3719 audiência OR audiência OR depoimento OR testemunha OR ata",
        "15547 audiência OR depoimento OR ata",
        "ext:mp3;m4a;wav;wma 3719",
        "ext:txt;docx;pdf \"Filipe Delgado\" depoimento OR declarações",
        "ext:txt;docx;pdf \"João Pedro\" depoimento OR declarações"
    ]

    for q in court_queries:
        res = query_everything(q, 10)
        total = res.get("totalResults", len(res.get("results", [])))
        print(f"[TRIBUNAL] '{q}' -> Total: {total}")
        for r in res.get("results", [])[:3]:
            p = r.get("path", "") + "\\" + r.get("name", "")
            print(f"   -> {p}")

if __name__ == "__main__":
    main()
