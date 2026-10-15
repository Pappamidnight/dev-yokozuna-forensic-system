# -*- coding: utf-8 -*-
r"""
acervo_master.py - Gera todos os JSON, valida, executa diagnosticos.
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime

DIR = r"C:\ACERVO\config"
ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"

# ============================================================
# DEFINICAO DOS 12 JSON
# ============================================================
CONFIGS = {
"01_sdk": {
  "id": "01_sdk",
  "classificacao": "infraestrutura",
  "prioridade": 1,
  "descricao": "Configuracao do Everything SDK (DLL)",
  "config": {
    "dll_path": r"C:\ACERVO\bin\SDK\Everything64.dll",
    "versao_minima": "3.0.0.9",
    "instancia": INST,
    "requer_gui_a_correr": True,
    "timeout_ipc_ms": 30000
  },
  "verificacao": "python -c \"import ctypes; ctypes.WinDLL(r'C:\\ACERVO\\bin\\SDK\\Everything64.dll'); print('OK')\"",
  "limitacoes": [
    "SDK3 so funciona com Everything 1.5.0.1397a ou superior",
    "Requer Everything GUI a correr",
    "Se Everything correr como admin, IPC v3 falha em versoes < 1.5.0.1419b"
  ]
},
"02_mcp": {
  "id": "02_mcp",
  "classificacao": "integracao_llm",
  "prioridade": 3,
  "descricao": "Servidores MCP",
  "implementacoes": [
    {
      "nome": "everything-mcp (in-process)",
      "autor": "Jotaro",
      "repositorio": "https://github.com/Jotaro2025/everything-mcp",
      "tipo": "plugin_dll",
      "dll": "everything_mcp64.dll"
    },
    {
      "nome": "Everything MCP Server",
      "autor": "Josephur",
      "tipo": "processo_externo",
      "depende_de": "HTTP Server plugin ativo",
      "config": {"host": "localhost", "porta": 80}
    }
  ],
  "config_global": {
    "path_plugins_everything": r"C:\Program Files\Everything\Plugins",
    "config_ini": "Plugins-1.5a.ini"
  }
},
"03_plugins": {
  "id": "03_plugins",
  "classificacao": "infraestrutura",
  "prioridade": 2,
  "descricao": "Plugins do Everything 1.5",
  "plugins": [
    {
      "nome": "HTTP Server",
      "versao": "1.0.5.6",
      "config": {"porta": 80, "host": "127.0.0.1", "autenticacao": False, "log_ativo": True},
      "endpoints": {
        "json": "http://localhost/?s=<query>&json=1",
        "com_colunas": "http://localhost/?s=<query>&json=1&path_column=1&size_column=1",
        "com_sort": "http://localhost/?s=<query>&json=1&sort=size&ascending=0"
      }
    },
    {"nome": "ETP/FTP Server", "versao": "1.0.2.5", "config": {"porta": 21}},
    {"nome": "Everything Server", "versao": "1.0.4.5"}
  ]
},
"04_cli_es": {
  "id": "04_cli_es",
  "classificacao": "motor_principal",
  "prioridade": 1,
  "descricao": "Configuracao do es.exe",
  "versao": "1.1.0.38",
  "instalacao": {"path_binario": ES, "instancia": INST},
  "exemplos": {
    "contar_pdfs": f"es.exe -instance {INST} -get-result-count \"ext:pdf\"",
    "tamanho_videos": f"es.exe -instance {INST} -get-total-size \"video:\"",
    "top_20_videos": f"es.exe -instance {INST} -n 20 -size -dm -sort size-descending \"video:\"",
    "duplicados": f"es.exe -instance {INST} \"video: dupe:size\"",
    "exportar_json": f"es.exe -instance {INST} -json -n 1000 \"ext:pdf\" > pdfs.json"
  }
},
"05_filtros": {
  "id": "05_filtros",
  "classificacao": "consultas",
  "prioridade": 2,
  "descricao": "Filtros combinados",
  "filtros": [
    {"nome": "Ficheiros muito grandes", "query": "size:>1gb"},
    {"nome": "Videos grandes", "query": "video: size:>100mb"},
    {"nome": "Imagens grandes", "query": "image: size:>10mb"},
    {"nome": "PDFs grandes", "query": "ext:pdf size:>10mb"},
    {"nome": "Ficheiros de sistema", "query": "attrib:S size:>500mb"},
    {"nome": "Ocultos grandes", "query": "attrib:H size:>500mb"},
    {"nome": "Modificados recentemente", "query": "dm:lastweek size:>100mb"},
    {"nome": "Antigos e grandes", "query": "dm:<2020 size:>500mb"},
    {"nome": "Duplicados de video", "query": "video: dupe:size"},
    {"nome": "Duplicados de imagem", "query": "image: dupe:name;size"},
    {"nome": "Fora do santuario", "query": "dupe-from:\"C:\\ACERVO\\storage\\\""},
    {"nome": "Temporarios", "query": "ext:tmp;temp;bak;old size:>10mb"},
    {"nome": "Downloads incompletos", "query": "ext:crdownload;part"}
  ]
},
"06_dicionarios": {
  "id": "06_dicionarios",
  "classificacao": "heuristica",
  "prioridade": 4,
  "descricao": "Dicionarios de sinonimos",
  "localizacao_ficheiro": "%APPDATA%\\Everything\\Synonyms-1.5a.txt",
  "formato": "termo;sinonimo1;sinonimo2",
  "dicionarios": {
    "color": ["colour", "cor", "cores", "colors"],
    "brasil": ["brazil", "br"],
    "config": ["configuration", "cfg", "settings"],
    "imagem": ["image", "img", "picture", "photo"],
    "video": ["movie", "film", "clip"],
    "documento": ["document", "doc", "file"],
    "manual": ["guide", "handbook"],
    "temp": ["temporario", "tmp"],
    "backup": ["bk", "bkp"],
    "relatorio": ["report", "reports"]
  }
},
"07_heuristica": {
  "id": "07_heuristica",
  "classificacao": "heuristica",
  "prioridade": 4,
  "descricao": "Regras heuristicas para agrupar variantes",
  "regras": {
    "video": [
      {"nome": "Series S01E01", "regex": "^(.*?)[. _\\-](?:s\\d{2}e\\d{2})"},
      {"nome": "Resolucao", "regex": "^(.*?)[. _\\-](?:1080p|720p|4k|2160p)"},
      {"nome": "Codec", "regex": "^(.*?)[. _\\-](?:x264|x265|hevc)"}
    ],
    "imagem": [
      {"nome": "Fotos de camera", "regex": "^(.*?)[. _\\-](?:img|dsc|pxl)[_\\-]?\\d+"},
      {"nome": "Fotos com data", "regex": "^(.*?)[. _\\-](\\d{4})[. _\\-](\\d{2})[. _\\-](\\d{2})"}
    ],
    "audio": [
      {"nome": "Faixas numeradas", "regex": "^(.*?)[. _\\-]\\d{2}[. _\\-]"},
      {"nome": "Com feat.", "regex": "^(.*?)[. _\\-](?:feat|ft)\\."}
    ],
    "pdf": [
      {"nome": "Com versao", "regex": "^(.*?)[. _\\-](?:v\\d+|final|draft)"}
    ],
    "markdown": [
      {"nome": "Ficheiros comuns", "regex": "^(.*?)[. _\\-](?:readme|changelog|license|todo)"}
    ]
  }
},
"08_regex": {
  "id": "08_regex",
  "classificacao": "heuristica",
  "prioridade": 4,
  "descricao": "Regex pre-construidas",
  "categorias": {
    "datas": {
      "ano": "(?:19|20)\\d{2}",
      "data_iso": "\\d{4}-\\d{2}-\\d{2}",
      "data_br": "\\d{2}[/-]\\d{2}[/-]\\d{4}",
      "hora": "\\d{2}[:h]\\d{2}"
    },
    "media": {
      "serie": "[sS]\\d{1,2}[eE]\\d{1,2}",
      "versao": "v\\d+(?:\\.\\d+)*"
    },
    "hashes": {
      "md5": "[a-fA-F0-9]{32}",
      "sha1": "[a-fA-F0-9]{40}",
      "sha256": "[a-fA-F0-9]{64}"
    },
    "duplicados": {
      "copia": "(?:copia|copy|\\bcopy\\b)",
      "final": "(?:final|vfinal|_final)",
      "backup": "(?:backup|bak|bkp)",
      "temp": "(?:temp|tmp|~)"
    }
  }
},
"09_workflows": {
  "id": "09_workflows",
  "classificacao": "workflow",
  "prioridade": 2,
  "descricao": "Workflows prontos",
  "workflows": [
    {"nome": "inventario_inicial", "passos": [
      f"es.exe -instance {INST} -get-result-count \"path:\\\"C:\\ACERVO\\\"\"",
      f"es.exe -instance {INST} -get-total-size \"path:\\\"C:\\ACERVO\\\"\""
    ]},
    {"nome": "analise_espaco", "passos": [
      f"es.exe -instance {INST} -n 50 -size -dm -sort size-descending \"size:>100mb\"",
      f"es.exe -instance {INST} -get-total-size \"video:\"",
      f"es.exe -instance {INST} -get-total-size \"image:\"",
      f"es.exe -instance {INST} -get-total-size \"audio:\""
    ]},
    {"nome": "deteccao_duplicados", "passos": [
      f"es.exe -instance {INST} -n 200 \"video: dupe:size\"",
      f"es.exe -instance {INST} -n 200 \"image: dupe:name;size\"",
      f"es.exe -instance {INST} -n 200 \"audio: dupe:size\"",
      f"es.exe -instance {INST} -n 200 \"ext:pdf dupe:name;size\""
    ]}
  ]
},
"10_dryrun": {
  "id": "10_dryrun",
  "classificacao": "workflow",
  "prioridade": 1,
  "descricao": "Regras de dry-run obrigatorio",
  "regras": [
    "Sempre --dry-run antes de --executar",
    "Sempre --raiz-only \"C:\\ACERVO\" para evitar mexer em G:\\",
    "Exportar EFU antes de qualquer operacao de escrita",
    "Nunca apagar — so mover para quarentena",
    "Nunca shutil.move entre drives",
    "Validar por hash no santuario",
    "Uma raiz de cada vez"
  ]
},
"11_consultas": {
  "id": "11_consultas",
  "classificacao": "consultas",
  "prioridade": 2,
  "descricao": "Consultas frequentes",
  "consultas": {
    "por_tamanho": {"maior_1gb": "size:>1gb", "vazio": "size:0"},
    "por_tipo": {"videos": "video:", "imagens": "image:", "pdfs": "ext:pdf"},
    "por_data": {"hoje": "dm:today", "esta_semana": "dm:lastweek", "antigos": "dm:<2020"},
    "por_atributo": {"ocultos": "attrib:H", "sistema": "attrib:S"},
    "duplicados": {"por_nome": "dupe:name", "por_tamanho": "dupe:size", "por_nome_tamanho": "dupe:name;size"},
    "fantasmas": {"geral": "!EXISTSONDISK($filename:)"}
  }
},
"12_classificacao": {
  "id": "12_classificacao",
  "classificacao": "meta",
  "prioridade": 1,
  "descricao": "Classificacao de ficheiros",
  "tipos": {
    "sistema": {"path": r"C:\Windows", "risco": "intocavel"},
    "pagefile_hiberfil": {"ficheiros": ["pagefile.sys", "hiberfil.sys"], "risco": "gerido pelo Windows"},
    "virtualizacao": {"extensoes": [".vhdx", ".vhd"], "risco": "dados de VM"},
    "media_video": {"extensoes": [".mp4", ".mkv", ".avi", ".mov"]},
    "media_imagem": {"extensoes": [".jpg", ".jpeg", ".png", ".gif", ".webp"]},
    "media_audio": {"extensoes": [".mp3", ".flac", ".wav", ".m4a"]},
    "documentos": {"extensoes": [".pdf", ".doc", ".docx", ".xls", ".xlsx"]},
    "codigo": {"extensoes": [".py", ".js", ".ts", ".ps1", ".sh", ".bat"]},
    "dados": {"extensoes": [".json", ".yaml", ".csv", ".db", ".duckdb"]},
    "backups": {"extensoes": [".zip", ".rar", ".7z", ".bak", ".old"]},
    "temporarios": {"extensoes": [".tmp", ".temp", ".crdownload", ".part"]}
  },
  "zonas_sensiveis": {
    r"C:\Windows": "intocavel",
    r"C:\Program Files": "intocavel",
    r"C:\ProgramData": "cuidado",
    r"C:\$Recycle.Bin": "intocavel",
    r"C:\System Volume Information": "intocavel"
  }
}
}

# ============================================================
# GRAVAR
# ============================================================
def gravar():
    os.makedirs(DIR, exist_ok=True)
    print("=" * 78)
    print("  A GRAVAR 12 JSON em " + DIR)
    print("=" * 78)
    for nome, cfg in CONFIGS.items():
        path = os.path.join(DIR, nome + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        tam = os.path.getsize(path)
        print(f"  [OK] {nome}.json ({tam:,} bytes)")

# ============================================================
# VALIDAR
# ============================================================
def validar():
    print()
    print("=" * 78)
    print("  VALIDACAO")
    print("=" * 78)
    ok = 0
    fail = 0
    for fname in sorted(os.listdir(DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tem_id = "id" in data
            tem_cls = "classificacao" in data
            tem_pri = "prioridade" in data
            if tem_id and tem_cls and tem_pri:
                print(f"  [OK]   {fname:<30} id={data['id']:<20} cls={data['classificacao']:<16} pri={data['prioridade']}")
                ok += 1
            else:
                print(f"  [WARN] {fname}: falta metadados")
                fail += 1
        except Exception as e:
            print(f"  [FAIL] {fname}: {e}")
            fail += 1
    print(f"\n  OK: {ok}  FAIL: {fail}")

# ============================================================
# DIAGNOSTICO ES.EXE
# ============================================================
def diag_es():
    print()
    print("=" * 78)
    print("  DIAGNOSTICO es.exe")
    print("=" * 78)
    if not os.path.isfile(ES):
        print(f"  [FAIL] es.exe nao existe em {ES}")
        return
    # Versao
    try:
        r = subprocess.run([ES, "-version"], capture_output=True, text=True, timeout=10)
        print(f"  Versao es.exe: {r.stdout.strip()}")
    except Exception as e:
        print(f"  [FAIL] versao: {e}")
    # Contagens
    queries = [
        ("Videos", "video:"),
        ("PDFs", "ext:pdf"),
        ("Imagens", "image:"),
        ("Audio", "audio:"),
        ("Total", ""),
    ]
    for nome, q in queries:
        t0 = time.time()
        try:
            r = subprocess.run(
                [ES, "-instance", INST, "-get-result-count", q],
                capture_output=True, text=True, timeout=60
            )
            n = r.stdout.strip()
            t = time.time() - t0
            print(f"  {nome:<10} {n:>12}  ({t:.2f}s)")
        except Exception as e:
            print(f"  {nome:<10} ERRO: {e}")

# ============================================================
# DIAGNOSTICO SDK
# ============================================================
def diag_sdk():
    print()
    print("=" * 78)
    print("  DIAGNOSTICO SDK")
    print("=" * 78)
    dll = r"C:\ACERVO\bin\SDK\Everything64.dll"
    if not os.path.isfile(dll):
        print(f"  [FAIL] DLL nao existe: {dll}")
        return
    tam = os.path.getsize(dll)
    print(f"  DLL: {dll} ({tam:,} bytes)")
    try:
        import ctypes
        h = ctypes.WinDLL(dll)
        print("  [OK] DLL carrega")
    except Exception as e:
        print(f"  [FAIL] DLL nao carrega: {e}")

# ============================================================
# MAIN
# ============================================================
def main():
    print()
    print("=" * 78)
    print("  ACERVO MASTER - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 78)
    gravar()
    validar()
    diag_es()
    diag_sdk()
    print()
    print("=" * 78)
    print("  CONCLUIDO")
    print("=" * 78)


if __name__ == "__main__":
    main()
