import urllib.request
import urllib.parse
import json

def search(q):
    url = "http://127.0.0.1:8080/?search=" + urllib.parse.quote(q) + "&json=1&count=20&path_column=1"
    try:
        req = urllib.request.urlopen(url, timeout=10)
        data = json.loads(req.read().decode("utf-8"))
        print(f"=== {q} (Total: {data.get('totalResults', 0)}) ===")
        for r in data.get("results", [])[:8]:
            print("  -", r.get("path", "") + "\\" + r.get("name", ""))
    except Exception as e:
        print(f"Erro em {q}: {e}")

def main():
    search("Varela")
    search("Varela Centenario")
    search("Varela arrombar")
    search("Centenário execução")
    search("Cleber Varela")

if __name__ == "__main__":
    main()
