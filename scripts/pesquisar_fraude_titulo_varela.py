import urllib.request
import urllib.parse
import json
from pathlib import Path

def search(q):
    url = "http://127.0.0.1:8080/?search=" + urllib.parse.quote(q) + "&json=1&count=10&path_column=1"
    try:
        req = urllib.request.urlopen(url, timeout=10)
        data = json.loads(req.read().decode("utf-8"))
        print(f"=== {q} (Total: {data.get('totalResults', 0)}) ===")
        for r in data.get("results", [])[:5]:
            p = r.get("path", "") + "\\" + r.get("name", "")
            print("  -", p)
            # Se for texto ou markdown, tentar ler trecho
            if p.endswith(".md") or p.endswith(".txt") or p.endswith(".json"):
                try:
                    txt = Path(p).read_text(encoding="utf-8", errors="ignore")
                    print("     [TRECHO]:", txt[:400].replace("\n", " "))
                except Exception as ex:
                    print("     [ERRO LEITURA]:", ex)
    except Exception as e:
        print(f"Erro em {q}: {e}")

def main():
    search("VARELA TITULO INEXISTENTE")
    search("CENTENARIO_2021-12-09_TERMO_AUTENTICACAO_VARELA")
    search("Transmissao de divida")
    search("Cleber Varela reuni")

if __name__ == "__main__":
    main()
