#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servidor_comparador_everything_lan.py
Servidor de Auditoria e Comparacao de Acervos Multi-PC via Everything HTTP API.
Desenvolvido para inspecao de computadores remotos na rede local (Ethernet / Wi-Fi)
referentes aos anos 2018, 2019, 2020, 2021, 2022 e 2023.

Porta de Operacao: 8088
Integracao Local: http://127.0.0.1:8080/ (Everything HTTP Local)
Base de Dados: C:\ACERVO\logs\comparador_lan_deltas.sqlite
"""

import os
import sys
import json
import socket
import sqlite3
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

DB_PATH = Path(r"C:\ACERVO\logs\comparador_lan_deltas.sqlite")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
EVERYTHING_LOCAL_URL = "http://127.0.0.1:8080"
PORTA_SERVIDOR = 8088

# Inicializar Base de Dados SQLite
def inicializar_bd():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nos_rede (
                ip TEXT PRIMARY KEY,
                nome TEXT,
                ano TEXT,
                status TEXT,
                total_ficheiros INTEGER,
                data_verificacao TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ficheiros_deltas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                no_origem_ip TEXT,
                caminho TEXT,
                nome TEXT,
                tamanho INTEGER,
                data_modificacao TEXT,
                extensao TEXT,
                existe_no_local INTEGER,
                ano_estimado TEXT,
                data_registo TEXT
            )
        """)
        conn.commit()

inicializar_bd()

def consultar_everything_http(base_url: str, query: str = "", count: int = 5000):
    """Consulta uma instancia do Everything via API HTTP (porta 8080)."""
    params = urllib.parse.urlencode({
        "search": query,
        "json": 1,
        "count": count,
        "path_column": 1,
        "size_column": 1,
        "date_modified_column": 1
    })
    url = f"{base_url.rstrip('/')}/?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AGY-Lan-Auditor/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                return data.get("results", [])
    except Exception as e:
        return None
    return []

def testar_no(ip: str, porta: int = 8080, timeout: float = 0.5):
    """Testa se existe um servico Everything ativo no IP indicado."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        res = sock.connect_ex((ip, porta))
        sock.close()
        if res == 0:
            # Testar se responde HTTP Everything
            url = f"http://{ip}:{porta}/?json=1&count=1"
            req = urllib.request.Request(url, headers={"User-Agent": "AGY-Lan-Auditor/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    total = data.get("totalResults", 0)
                    return {"ip": ip, "porta": porta, "ativo": True, "total": total}
    except Exception:
        pass
    return None

def obter_ips_locais():
    """Descobre a gama de IPs da sub-rede local (ex: 192.168.1.x)."""
    subnets = []
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                partes = ip.split(".")
                if len(partes) == 4:
                    subnets.append(".".join(partes[:3]))
    except Exception:
        pass
    if not subnets:
        subnets = ["192.168.1"]
    return list(set(subnets))

def varrer_rede_local():
    """Varre os 254 enderecos de cada sub-rede a procura do Everything na porta 8080."""
    subnets = obter_ips_locais()
    nos_encontrados = []
    ips_para_testar = []
    for sub in subnets:
        for i in range(1, 255):
            ips_para_testar.append(f"{sub}.{i}")
    
    with ThreadPoolExecutor(max_workers=60) as executor:
        resultados = executor.map(testar_no, ips_para_testar)
        for r in resultados:
            if r and r.get("ativo"):
                nos_encontrados.append(r)
    return nos_encontrados

def comparar_acervo_remoto(ip_remoto: str, ano_alvo: str = "TODOS"):
    """Compara os ficheiros do PC remoto com o Everything local e extrai os ficheiros em falta."""
    query = ""
    if ano_alvo != "TODOS":
        query = f"dm:{ano_alvo}"
    
    # 1. Obter ficheiros do no remoto
    remotos = consultar_everything_http(f"http://{ip_remoto}:8080", query=query, count=10000)
    if remotos is None:
        return {"erro": f"Impossivel conectar a http://{ip_remoto}:8080/"}
    
    # 2. Obter inventario local para os mesmos termos
    locais = consultar_everything_http(EVERYTHING_LOCAL_URL, query=query, count=20000)
    locais_nomes_tamanhos = set()
    if locais:
        for f in locais:
            locais_nomes_tamanhos.add((f.get("name", "").lower(), f.get("size", 0)))
    
    deltas = []
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        agora = datetime.now().isoformat()
        
        for f in remotos:
            nome = f.get("name", "")
            tamanho = f.get("size", 0)
            caminho = f.get("path", "")
            data_mod = str(f.get("date_modified", ""))
            ext = Path(nome).suffix.lower()
            
            # Se nao existe localmente com o mesmo nome e tamanho
            existe = 1 if (nome.lower(), tamanho) in locais_nomes_tamanhos else 0
            
            if existe == 0:
                deltas.append({
                    "no_ip": ip_remoto,
                    "caminho": caminho,
                    "nome": nome,
                    "tamanho": tamanho,
                    "data_mod": data_mod,
                    "extensao": ext,
                    "ano": ano_alvo
                })
                cursor.execute("""
                    INSERT INTO ficheiros_deltas 
                    (no_origem_ip, caminho, nome, tamanho, data_modificacao, extensao, existe_no_local, ano_estimado, data_registo)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """, (ip_remoto, caminho, nome, tamanho, data_mod, ext, ano_alvo, agora))
        
        cursor.execute("""
            INSERT OR REPLACE INTO nos_rede (ip, nome, ano, status, total_ficheiros, data_verificacao)
            VALUES (?, ?, ?, 'CONECTADO', ?, ?)
        """, (ip_remoto, f"PC_REMOTO_{ip_remoto}", ano_alvo, len(remotos), agora))
        conn.commit()

    return {
        "ip_remoto": ip_remoto,
        "total_remoto": len(remotos),
        "total_em_falta_localmente": len(deltas),
        "amostra_deltas": deltas[:100]
    }

class RequisicaoHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.gerar_html().encode("utf-8"))

        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = {
                "local_everything": "ONLINE" if consultar_everything_http(EVERYTHING_LOCAL_URL, count=1) is not None else "OFFLINE",
                "servidor": "ATIVO",
                "porta": PORTA_SERVIDOR,
                "ips_locais": obter_ips_locais(),
                "base_dados": str(DB_PATH)
            }
            self.wfile.write(json.dumps(status).encode("utf-8"))

        elif path == "/api/varrer_rede":
            nos = varrer_rede_local()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"nos": nos}).encode("utf-8"))

        elif path == "/api/comparar":
            ip = params.get("ip", [""])[0]
            ano = params.get("ano", ["TODOS"])[0]
            if not ip:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"erro": "IP obrigatorio"}')
                return
            res = comparar_acervo_remoto(ip, ano)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif path == "/api/deltas":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, no_origem_ip, caminho, nome, tamanho, extensao, ano_estimado, data_registo 
                    FROM ficheiros_deltas ORDER BY id DESC LIMIT 500
                """)
                rows = [dict(r) for r in cursor.fetchall()]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"deltas": rows}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def gerar_html(self):
        return """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGY Forense — Auditor e Comparador de Acervos Multi-PC (2018–2023)</title>
    <style>
        :root {
            --bg: #0b0f19;
            --surface: #141b2d;
            --surface-hover: #1f293d;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.2);
            --accent: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #f3f4f6;
            --text-dim: #9ca3af;
            --border: #243048;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        body { background: var(--bg); color: var(--text); padding: 24px; min-height: 100vh; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
        h1 { font-size: 1.4rem; font-weight: 600; color: #fff; letter-spacing: -0.5px; display: flex; align-items: center; gap: 10px; }
        .badge { padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
        .badge-online { background: rgba(16, 185, 129, 0.2); color: var(--accent); border: 1px solid rgba(16, 185, 129, 0.4); }
        .grid { display: grid; grid-template-columns: 350px 1fr; gap: 24px; }
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .card h2 { font-size: 1.05rem; font-weight: 600; margin-bottom: 16px; color: var(--primary); border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 0.8rem; color: var(--text-dim); margin-bottom: 6px; font-weight: 500; }
        input, select { width: 100%; background: #0f1523; border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; color: #fff; font-size: 0.9rem; }
        input:focus, select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-glow); }
        button { width: 100%; background: var(--primary); color: #0b0f19; font-weight: 600; border: none; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
        button:hover { filter: brightness(1.1); transform: translateY(-1px); }
        button.secondary { background: var(--surface-hover); color: var(--text); border: 1px solid var(--border); margin-top: 8px; }
        button.secondary:hover { background: #28354f; }
        .table-container { overflow-x: auto; max-height: 600px; border-radius: 8px; border: 1px solid var(--border); }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }
        th { background: #1a233a; padding: 12px; color: var(--text-dim); font-weight: 600; position: sticky; top: 0; }
        td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
        tr:hover { background: var(--surface-hover); }
        .tag { padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }
        .tag-delta { background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.4); }
        .status-box { padding: 12px; border-radius: 8px; background: #0f1523; border: 1px solid var(--border); font-size: 0.85rem; margin-top: 14px; line-height: 1.5; }
        .btn-anos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 8px; }
        .btn-ano { background: var(--surface-hover); color: var(--text); border: 1px solid var(--border); padding: 8px; font-size: 0.8rem; border-radius: 6px; cursor: pointer; text-align: center; }
        .btn-ano:hover, .btn-ano.active { background: var(--primary); color: #0b0f19; font-weight: 700; }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>AGY FORENSE — AUDITOR E COMPARADOR MULTI-PC</h1>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-top: 4px;">Inspeção de Acervos via Everything HTTP na Rede Local (Ethernet / LAN 192.168.1.X)</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="badge badge-online" id="status-everything">Everything Local: Conectado</span>
            <span class="badge" style="background: rgba(56,189,248,0.2); color: var(--primary); border: 1px solid var(--primary);">Porta 8088</span>
        </div>
    </header>

    <div class="grid">
        <div class="card">
            <h2>Conexão com PC Remoto</h2>
            <div class="form-group">
                <label>IP do PC na Rede (Ethernet / Wi-Fi):</label>
                <input type="text" id="ip-remoto" placeholder="Ex: 192.168.1.50 ou 192.168.1.100" value="192.168.1.">
            </div>

            <div class="form-group">
                <label>Filtro Temporal por Ano:</label>
                <div class="btn-anos">
                    <div class="btn-ano" onclick="selecionarAno('2018', this)">2018</div>
                    <div class="btn-ano" onclick="selecionarAno('2019', this)">2019</div>
                    <div class="btn-ano" onclick="selecionarAno('2020', this)">2020</div>
                    <div class="btn-ano" onclick="selecionarAno('2021', this)">2021</div>
                    <div class="btn-ano" onclick="selecionarAno('2022', this)">2022</div>
                    <div class="btn-ano" onclick="selecionarAno('2023', this)">2023</div>
                </div>
                <input type="hidden" id="ano-alvo" value="TODOS">
            </div>

            <button onclick="compararPC()">Auditar e Extrair Ficheiros em Falta</button>
            <button class="secondary" onclick="varrerRede()">Varrer Rede Local (Descobrir PCs)</button>

            <div class="status-box" id="info-box">
                <b>Pronto para auditoria.</b><br>
                Insira o IP do computador de 2018 a 2023 ou clique em 'Varrer Rede Local' para identificar instâncias ativas do Everything na porta 8080.
            </div>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h2>Deltas Encontrados (Ficheiros no Outro PC Que Não Existem Neste)</h2>
                <span id="contador-deltas" class="tag tag-delta">0 Ficheiros Registados</span>
            </div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>PC Origem</th>
                            <th>Nome do Ficheiro</th>
                            <th>Extensão</th>
                            <th>Tamanho</th>
                            <th>Caminho Original</th>
                        </tr>
                    </thead>
                    <tbody id="tabela-deltas">
                        <tr>
                            <td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">
                                Nenhum delta carregado. Inicie a auditoria ao PC remoto para identificar acervos em falta.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let anoSelecionado = "TODOS";

        function selecionarAno(ano, el) {
            document.querySelectorAll('.btn-ano').forEach(b => b.classList.remove('active'));
            if (anoSelecionado === ano) {
                anoSelecionado = "TODOS";
            } else {
                anoSelecionado = ano;
                el.classList.add('active');
            }
            document.getElementById('ano-alvo').value = anoSelecionado;
        }

        async function varrerRede() {
            const info = document.getElementById('info-box');
            info.innerHTML = "<b>A varrer a sub-rede local...</b><br>A testar portas 8080 em 192.168.1.1 a 192.168.1.254...";
            try {
                const resp = await fetch('/api/varrer_rede');
                const data = await resp.json();
                if (data.nos && data.nos.length > 0) {
                    let html = "<b>PCs com Everything Encontrados:</b><br>";
                    data.nos.forEach(n => {
                        html += `• IP <b>${n.ip}</b> (${n.total} ficheiros indexados) <button style="width: auto; padding: 2px 8px; margin-left: 6px; font-size: 0.75rem;" onclick="definirIP('${n.ip}')">Selecionar</button><br>`;
                    });
                    info.innerHTML = html;
                } else {
                    info.innerHTML = "<b>Varredura concluída:</b> Nenhum outro Everything HTTP detetado automaticamente. Verifique se o Everything está aberto no outro PC com a opção 'HTTP Server' ativa nas opções, ou insira o IP diretamente.";
                }
            } catch (err) {
                info.innerHTML = "Erro ao varrer a rede: " + err;
            }
        }

        function definirIP(ip) {
            document.getElementById('ip-remoto').value = ip;
        }

        async function compararPC() {
            const ip = document.getElementById('ip-remoto').value.trim();
            const ano = document.getElementById('ano-alvo').value;
            const info = document.getElementById('info-box');
            if (!ip || ip === "192.168.1.") {
                alert("Por favor indique um IP válido.");
                return;
            }
            info.innerHTML = `<b>A conectar ao PC ${ip}...</b><br>A descarregar inventário e a cruzar com o Everything local...`;
            
            try {
                const resp = await fetch(`/api/comparar?ip=${encodeURIComponent(ip)}&ano=${encodeURIComponent(ano)}`);
                const data = await resp.json();
                if (data.erro) {
                    info.innerHTML = `<span style="color: var(--danger)"><b>Erro:</b> ${data.erro}</span>`;
                    return;
                }
                info.innerHTML = `<b>Auditoria Concluída com Sucesso!</b><br>` +
                    `• Total no PC remoto: <b>${data.total_remoto}</b> ficheiros<br>` +
                    `• Ficheiros em falta neste PC: <b style="color: var(--warning)">${data.total_em_falta_localmente}</b>`;
                carregarDeltas();
            } catch (err) {
                info.innerHTML = "Erro ao comparar: " + err;
            }
        }

        async function carregarDeltas() {
            const resp = await fetch('/api/deltas');
            const data = await resp.json();
            const tbody = document.getElementById('tabela-deltas');
            const contador = document.getElementById('contador-deltas');
            
            if (!data.deltas || data.deltas.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">Nenhum ficheiro em falta detetado.</td></tr>`;
                contador.textContent = "0 Ficheiros Registados";
                return;
            }

            contador.textContent = `${data.deltas.length} Ficheiros em Falta Registados`;
            let html = "";
            data.deltas.forEach(d => {
                const tamKb = (d.tamanho / 1024).toFixed(1) + " KB";
                html += `<tr>
                    <td><b>${d.no_origem_ip}</b></td>
                    <td style="color: var(--primary); font-weight: 500;">${d.nome}</td>
                    <td><span class="tag tag-delta">${d.extensao || '—'}</span></td>
                    <td>${tamKb}</td>
                    <td style="color: var(--text-dim); font-size: 0.75rem;">${d.caminho}</td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        // Carregar status e deltas iniciais
        carregarDeltas();
    </script>
</body>
</html>
"""

def main():
    server_address = ("0.0.0.0", PORTA_SERVIDOR)
    httpd = HTTPServer(server_address, RequisicaoHandler)
    print("=" * 70)
    print(f"AGY FORENSE — SERVIDOR COMPARADOR MULTI-PC INICIADO")
    print(f"Porta HTTP Local: {PORTA_SERVIDOR}")
    print(f"Acesso Local: http://localhost:{PORTA_SERVIDOR}")
    print(f"Acesso na Rede (Ethernet): http://192.168.1.95:{PORTA_SERVIDOR}")
    print(f"Base de Dados SQLite: {DB_PATH}")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo operador.")

if __name__ == "__main__":
    main()
