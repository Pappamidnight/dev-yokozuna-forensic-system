#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_forensic_server.py - Servidor MCP (Model Context Protocol) para OpenCode, Qwen e Antigravity.
Disponibiliza ferramentas de acesso ao sistema de ficheiros forense, base SQLite e RAG Juridico via stdio (JSON-RPC 2.0).
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
TRIBUNAL_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL"

# Importar o RAG Juridico local
sys.path.append(str(DEV_ROOT / "Backend"))
try:
    from legal_rag_knowledge_base import LegalRagEngine
    rag_engine = LegalRagEngine()
except Exception:
    rag_engine = None

TOOLS_DEFINITIONS = [
    {
        "name": "search_evidence",
        "description": "Pesquisa por documentos, faturas, certidões e ficheiros na base de dados forense SQLite (+133k evidências).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Termo de pesquisa (Ex: Galp, Epal, Fatura 82k, Acordao, Luisa Santos)"},
                "limit": {"type": "integer", "description": "Número máximo de resultados (padrão: 20)", "default": 20}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_process_status",
        "description": "Obtém o estado oficial no Citius e resumo probatório de um dos processos (23142, 3719, 10153, 20203 ou 15547).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_id": {"type": "string", "description": "Número ou sufixo do processo (Ex: 23142, 3719, 10153, 15547)"}
            },
            "required": ["process_id"]
        }
    },
    {
        "name": "query_legal_rag",
        "description": "Consulta a Base de Conhecimento e o Motor RAG de 4 Camadas para obter fundamentação jurídica e factos provados.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Questão jurídica ou factual sobre os processos."}
            },
            "required": ["question"]
        }
    },
    {
        "name": "list_court_documents",
        "description": "Lista os ficheiros oficiais do tribunal (Citius) disponíveis na pasta do processo correspondente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_folder": {"type": "string", "description": "Nome ou parte da pasta (Ex: 23142, 3719, 10153, 15547)"}
            }
        }
    }
]

def handle_search_evidence(args: Dict[str, Any]) -> str:
    q = args.get("query", "")
    limit = args.get("limit", 20)
    if not DB_PATH.exists():
        return "Base de dados SQLite não encontrada."
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria, sha256 
    FROM evidencias 
    WHERE filename LIKE ? OR filepath LIKE ? 
    ORDER BY size_bytes DESC LIMIT ?
    """, (f"%{q}%", f"%{q}%", limit))
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        return f"Nenhuma evidência encontrada para '{q}'."
        
    out = [f"Resultados encontrados ({len(rows)}):"]
    for r in rows:
        out.append(f"- [{r[3]}] {r[0]} ({r[2]} bytes) -> {r[1]}")
    return "\n".join(out)

def handle_get_process_status(args: Dict[str, Any]) -> str:
    pid = args.get("process_id", "")
    if "23142" in pid:
        return "Processo 23142/22.7T8LSB: JULGADA EXTINTA PELO TRL. Ordem de levantamento de penhoras (€ 35.000 + veículos). Confissão da AE Luísa Santos de nulidade de citação em 20/09/2024."
    elif "3719" in pid:
        return "Processo 3719/25.0T8LSB: PROCESSO ARQUIVADO DEFINITIVAMENTE. Acórdão TRL a 16/04/2026 (Ref. 24500137); Autora Maria Teresa Martins condenada em custas a 07/07/2026 (Ref. 457395171); Direito de Retenção e 12 Vídeos de vistoria."
    elif "10153" in pid:
        return "Processo 10153/24.7T8LSB: EXECUÇÃO SUSPENSA (Artigo 733.º CPC em 23/10/2025). Despacho Liminar do Juiz 8 proibiu penhoras. TPA afeto à LEA (PS 1-1064222419), € 52.285 retidos e Fatura € 82.722."
    elif "20203" in pid:
        return "Processo 20203/22.6T8LSB: Ação Declarativa Originária UNICRE. Nulidade absoluta de citação (duas cartas postais devolvidas e certidões negativas da AE Maria Emília Catrau)."
    elif "15547" in pid:
        return "Processo 15547/26.0T8LSB: Ação de Reivindicação. Petição de 12/06/2026; Citação postal devolvida em 24/07/2026; Citação delegada pelo Solicitador Ricardo Miranda a 04/08/2026. Defesa: 20+ contratos, 8 cadernetas e posse >10 anos."
    return f"Processo '{pid}' não reconhecido. Opções: 23142, 3719, 10153, 20203, 15547."

def handle_query_legal_rag(args: Dict[str, Any]) -> str:
    q = args.get("question", "")
    if rag_engine:
        res = rag_engine.query_rag(q)
        return res["resposta"]
    return "Motor RAG não disponível."

def handle_list_court_documents(args: Dict[str, Any]) -> str:
    folder_filter = args.get("process_folder", "")
    if not TRIBUNAL_DIR.exists():
        return "Pasta de arquivo do tribunal não encontrada."
    
    matching_files = []
    for d in TRIBUNAL_DIR.iterdir():
        if d.is_dir() and folder_filter.lower() in d.name.lower():
            files = list(d.glob("*"))
            matching_files.append(f"📁 Pasta: {d.name} ({len(files)} ficheiros):")
            for f in files[:15]:
                matching_files.append(f"  • {f.name} ({f.stat().st_size} bytes)")
    
    return "\n".join(matching_files) if matching_files else f"Nenhum documento encontrado para o filtro '{folder_filter}'."

def process_mcp_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    method = msg.get("method")
    msg_id = msg.get("id")
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_DEFINITIONS}
        }
    
    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        content_text = ""
        if tool_name == "search_evidence":
            content_text = handle_search_evidence(tool_args)
        elif tool_name == "get_process_status":
            content_text = handle_get_process_status(tool_args)
        elif tool_name == "query_legal_rag":
            content_text = handle_query_legal_rag(tool_args)
        elif tool_name == "list_court_documents":
            content_text = handle_list_court_documents(tool_args)
        else:
            content_text = f"Ferramenta desconhecida: {tool_name}"
            
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": content_text}]
            }
        }
    
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Forensic-Legal-MCP-Server", "version": "2.1.0"}
            }
        }
        
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {}
    }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = process_mcp_message(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
