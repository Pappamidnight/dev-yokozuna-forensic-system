# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

def testar(q):
    try:
        url = "http://localhost:8080/?search=" + urllib.parse.quote(q) + "&json=1&count=1"
        r = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
        d = json.loads(r)
        total = d.get("totalResults", 0)
        print(f"  {total:>10,}  <-  {q}")
    except Exception as e:
        print(f"  [ERRO] {q}: {e}")

print("=" * 70)
print("  TESTE DE SINTAXE - EVERYTHING HTTP")
print("=" * 70)

queries = [
    'path:"G:\\O meu disco\\"',
    '"G:\\O meu disco\\"',
    'parent:"G:\\O meu disco"',
    'G:\\O meu disco',
    'path:G:',
    'path:"G:"',
    'G:',
    '*.pdf path:G:',
    'path:"G:\\O meu disco" *.pdf',
    'ext:pdf path:G:',
    'folder:G:\\',
]

for q in queries:
    testar(q)

print("=" * 70)
