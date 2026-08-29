#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ajax_forensic_server.py - Servidor Backend HTTP com RAG Juridico, Base de Conhecimento e Suporte AJAX Assincrono.
"""

import os
import sys
import json
import sqlite3
import mimetypes
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
STATIC_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

sys.path.append(str(DEV_ROOT / "Backend"))
try:
    from legal_rag_knowledge_base import LegalRagEngine
    rag_engine = LegalRagEngine()
except Exception:
    rag_engine = None

PROCESSOS_DATA = [
    {
        "id": "23142",
        "numero": "23142/22.7T8LSB",
        "tribunal": "Tribunal Judicial de Lisboa / Tribunal da Relação",
        "especie": "Execução de Sentença (Centenário)",
        "estado": "JULGADA EXTINTA PELO TRL",
        "badge_color": "#22c55e",
        "resumo": "Acórdão do TRL extinguiu a execução; Reclamação CAAJ e Queixa-Crime contra AE Luísa Santos (Cédula 5840); Áudios comprovam coação de Filipe Delgado e Dr. Varela.",
        "peca": "RECLAMACAO_CAAJ_E_QUADRO_FINANCEIRO_PROVAS.md"
    },
    {
        "id": "3719",
        "numero": "3719/25.0T8LSB",
        "tribunal": "Juízo Central Cível de Lisboa (Juiz 4) / TRL",
        "especie": "Procedimento Cautelar de Restituição de Posse",
        "estado": "PROCESSO ARQUIVADO DEFINITIVAMENTE",
        "badge_color": "#38bdf8",
        "resumo": "Acórdão da Relação de Lisboa de 16/04/2026 (Ref. 24500137); Processo baixou à 1.ª Instância e está ARQUIVADO; Autora condenada em custas a 07/07/2026; Corte seletivo de água por 2 anos.",
        "peca": "08.9_CONTRA_ALEGACOES_RECURSO_SENHORIA_COMPLETAS.md"
    },
    {
        "id": "10153",
        "numero": "10153/24.7T8LSB",
        "tribunal": "Juízo de Execução de Lisboa (Juiz 8)",
        "especie": "Execução Sentença (UNICRE) c/ Embargos Apensos",
        "estado": "EXECUÇÃO SUSPENSA (Art. 733.º CPC)",
        "badge_color": "#f59e0b",
        "resumo": "Despacho do Juiz 8 a 23/10/2025 suspendeu formalmente a execução e proibiu penhoras; Nulidade de citação no Proc. 20203/22; Fatura 82.722 € e Extratos de 33.900 €.",
        "peca": "DOSSIER_FINPARTNER_UNICRE_FATURA_82K.md"
    },
    {
        "id": "15547",
        "numero": "15547/26.0T8LSB",
        "tribunal": "Juízo Central Cível de Lisboa",
        "especie": "Ação Declarativa Comum (Reivindicação)",
        "estado": "CITAÇÃO DELEGADA A AGENTE DE EXECUÇÃO",
        "badge_color": "#a855f7",
        "resumo": "Petição de 12/06/2026; Citação postal devolvida a 24/07/2026; Solicitador Ricardo Miranda delegou ato a 04/08/2026; Defesa amparada em 20+ contratos e posse >10 anos.",
        "peca": "ANALISE_TRAMITACAO_CITIUS_PROC_15547.md"
    }
]

def rag_query(question: str) -> dict:
    if rag_engine:
        return rag_engine.query_rag(question)
    return {
        "query": question,
        "resposta": "Base de conhecimento não carregada.",
        "fontes": []
    }

class AjaxForensicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/status"):
            self.send_json_response(self.get_status_data())
            return

        if path.startswith("/api/search"):
            q = query.get("q", [""])[0]
            proc = query.get("proc", [""])[0]
            results = self.search_database(q, proc)
            self.send_json_response({"query": q, "total": len(results), "results": results})
            return

        if path.startswith("/api/processos"):
            self.send_json_response({"processos": PROCESSOS_DATA})
            return

        if path.startswith("/api/rag/ask"):
            q = query.get("q", [""])[0]
            self.send_json_response(rag_query(q))
            return

        file_path = STATIC_DIR / ("AJAX_PORTAL_FORENSE.html" if path in ["/", "/index.html"] else path.lstrip("/"))
        if file_path.exists() and file_path.is_file():
            self.serve_static_file(file_path)
            return

        self.send_error(404, f"Ficheiro nao encontrado: {path}")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/rag/ask"):
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            try:
                data = json.loads(body)
                q = data.get("query", "")
                self.send_json_response(rag_query(q))
                return
            except Exception:
                pass
            self.send_json_response(rag_query(""))
            return

        self.send_error(404, "Endpoint POST nao suportado")

    def serve_static_file(self, filepath: Path):
        try:
            content_type, _ = mimetypes.guess_type(str(filepath))
            if not content_type:
                content_type = "text/html" if filepath.suffix == ".html" else "application/octet-stream"
            
            with open(filepath, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Erro interno ao ler ficheiro: {e}")

    def send_json_response(self, data):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def get_status_data(self):
        total_files = 0
        total_hashes = 0
        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM evidencias")
                total_files = cur.fetchone()[0]
                cur.execute("SELECT COUNT(DISTINCT sha256) FROM evidencias WHERE sha256 IS NOT NULL AND sha256 != ''")
                total_hashes = cur.fetchone()[0]
                conn.close()
            except Exception:
                pass

        return {
            "status": "ONLINE",
            "rag_status": "READY",
            "total_files": total_files,
            "total_hashes": total_hashes,
            "processos_count": len(PROCESSOS_DATA),
            "processos": PROCESSOS_DATA
        }

    def search_database(self, query_str: str, proc_filter: str = ""):
        if not DB_PATH.exists():
            return []
        results = []
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cur = conn.cursor()
            sql = "SELECT filename, filepath, size_bytes, categoria, sha256 FROM evidencias WHERE 1=1"
            params = []
            if query_str:
                sql += " AND (filename LIKE ? OR filepath LIKE ?)"
                params.extend([f"%{query_str}%", f"%{query_str}%"])
            if proc_filter:
                sql += " AND (filename LIKE ? OR filepath LIKE ?)"
                params.extend([f"%{proc_filter}%", f"%{proc_filter}%"])
            sql += " ORDER BY size_bytes DESC LIMIT 40"
            cur.execute(sql, params)
            for r in cur.fetchall():
                results.append({
                    "filename": r[0],
                    "filepath": r[1],
                    "size_bytes": r[2],
                    "categoria": r[3],
                    "sha256": r[4] or ""
                })
            conn.close()
        except Exception:
            pass
        return results

def run_server(port=8088):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AjaxForensicHandler)
    print("=" * 80)
    print(f" SERVIDOR FORENSE & RAG JURIDICO INTEGRADO EM: http://localhost:{port}/")
    print(f" Diretorio Base: {STATIC_DIR}")
    print("=" * 80)
    httpd.serve_forever()

if __name__ == "__main__":
    port = 8088
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
