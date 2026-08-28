#!/usr/bin/env python3
"""
Gestor de Integração com o GitHub com Progresso em Tempo Real (github_manager.py).
Autentica com PAT, vincula o repositório e efetua o push com streaming de logs.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Yokozuna-Forensic-Agent"
}

def get_user_info():
    req = urllib.request.Request("https://api.github.com/user", headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data
    except urllib.error.HTTPError as exc:
        print(f"[ERRO HTTP {exc.code}]: {exc.read().decode()}", flush=True)
        return None
    except Exception as exc:
        print(f"[EXCECAO]: {exc}", flush=True)
        return None

def create_or_get_repo(repo_name="dev-yokozuna-forensic-system", private=True):
    user_data = get_user_info()
    if not user_data:
        return None, None

    username = user_data.get("login")
    print(f"[INFO] Autenticado no GitHub como: @{username} ({user_data.get('name') or username})", flush=True)

    check_url = f"https://api.github.com/repos/{username}/{repo_name}"
    req_check = urllib.request.Request(check_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req_check) as resp:
            data = json.loads(resp.read().decode())
            print(f"[INFO] Repositorio existente encontrado: {data.get('html_url')}", flush=True)
            return username, data
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"[INFO] Repositorio '{repo_name}' ainda nao existe. A criar novo repositorio...", flush=True)
        else:
            print(f"[ERRO HTTP {exc.code}]: {exc.read().decode()}", flush=True)

    payload = json.dumps({
        "name": repo_name,
        "description": "Ecossistema Forense, Societario e Multiagente Pydantic AI — Dev Yokozuna",
        "private": private,
        "auto_init": False
    }).encode()

    req_create = urllib.request.Request("https://api.github.com/user/repos", data=payload, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req_create) as resp:
            data = json.loads(resp.read().decode())
            print(f"[SUCESSO] Repositorio criado no GitHub: {data.get('html_url')}", flush=True)
            return username, data
    except urllib.error.HTTPError as exc:
        print(f"[ERRO ao criar repositorio HTTP {exc.code}]: {exc.read().decode()}", flush=True)
        return username, None

def run_cmd_stream(cmd, desc):
    print(f"\n[EXEC] {desc} ...", flush=True)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    if proc.stdout:
        for line in proc.stdout:
            print(line, end="", flush=True)
    proc.wait()
    return proc.returncode

def main():
    print("==================================================================", flush=True)
    print("INICIANDO PUBLICACAO AUTOMATICA NO GITHUB (DEV YOKOZUNA)", flush=True)
    print("==================================================================", flush=True)

    username, repo_data = create_or_get_repo("dev-yokozuna-forensic-system", private=True)
    if not username:
        print("[ERRO] Falha na autenticacao.", flush=True)
        return

    repo_url = f"https://{username}:{TOKEN}@github.com/{username}/dev-yokozuna-forensic-system.git"
    public_url = f"https://github.com/{username}/dev-yokozuna-forensic-system"

    os.chdir(DEV_ROOT)

    # 1. Configurar remote
    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

    # 2. Configurar buffer HTTP
    subprocess.run(["git", "config", "http.postBuffer", "524288000"], check=True)
    subprocess.run(["git", "config", "core.longpaths", "true"], check=True)

    # 3. Push da branch main
    ret_main = run_cmd_stream(["git", "push", "-u", "origin", "main", "--force"], "A enviar branch 'main' para o GitHub")

    # 4. Push das tags
    ret_tags = run_cmd_stream(["git", "push", "origin", "--tags", "--force"], "A enviar tags de versao (v1.0.0, v2.0.0, v2.5.0, v3.0.0)")

    print(f"\n==================================================================", flush=True)
    if ret_main == 0:
        print(f"[SUCESSO TOTAL] Codigo e versoes publicados com exito em:", flush=True)
        print(f"👉 {public_url}", flush=True)
    else:
        print(f"[AVISO] Ocorreu um erro no upload. Verifique as mensagens acima.", flush=True)
    print(f"==================================================================\n", flush=True)

if __name__ == "__main__":
    main()
