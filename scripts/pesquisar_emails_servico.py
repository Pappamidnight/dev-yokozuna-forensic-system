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
        print(f"Erro: {e}")
        return {}

def main():
    queries = [
        "path:Provas_Emails",
        "ext:eml | ext:msg | ext:mbox",
        "Palmeira <email | msg | whatsapp>",
        "\"Lisbon Experience\" <serviço | trabalho | comiss | fatura | ordenado>"
    ]
    for q in queries:
        res = query_everything(q, 15)
        print(f"Query '{q}' -> Total: {res.get('totalResults', len(res.get('results', [])))}")
        for r in res.get("results", [])[:5]:
            print("  -", r.get("path", "") + "\\" + r.get("name", ""))

if __name__ == "__main__":
    main()
