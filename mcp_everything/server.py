# -*- coding: utf-8 -*-
"""
server.py - MCP Server para Everything
========================================
Expõe ferramentas do Everything via Model Context Protocol.

Uso:
    python server.py

Configurar no cliente LLM (Claude Desktop, Cursor, etc):
    {
      "mcpServers": {
        "everything": {
          "command": "python",
          "args": ["C:\\\\ACERVO\\\\mcp_everything\\\\server.py"]
        }
      }
    }
"""
import sys
import json
import logging
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERRO: instalar mcp: pip install mcp", file=sys.stderr)
    sys.exit(1)

import tools


# ============================================================
# SETUP
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger(__name__)

app = Server("everything-mcp")


# ============================================================
# LISTAR TOOLS
# ============================================================
@app.list_tools()
async def list_tools():
    tool_list = []

    tool_defs = {
        "everything_search": {
            "description": "Pesquisa ficheiros no Everything. Usa sintaxe do Everything (ext:pdf, size:>10mb, dm:today, dupe:, !EXISTSONDISK, etc).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Sintaxe do Everything"},
                    "limit": {"type": "integer", "default": 100},
                    "source": {"type": "string", "enum": ["es", "sdk", "http"], "default": "es"},
                },
                "required": ["query"],
            },
        },
        "everything_count": {
            "description": "Conta quantos ficheiros correspondem a uma query.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        "everything_size": {
            "description": "Tamanho total (bytes) dos ficheiros.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        "everything_top": {
            "description": "Top N ficheiros maiores.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "n": {"type": "integer", "default": 20},
                },
                "required": ["query"],
            },
        },
        "everything_dupes": {
            "description": "Encontra duplicados por nome+tamanho.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                },
                "required": ["query"],
            },
        },
        "everything_ghosts": {
            "description": "Conta ghost entries (no indice mas nao no disco).",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "everything_efu": {
            "description": "Exporta resultado como EFU.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "output_path": {"type": "string"},
                },
                "required": ["query", "output_path"],
            },
        },
        "everything_version": {
            "description": "Versao do es.exe e do SDK.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "filesystem_scan": {
            "description": "Scan rapido de uma pasta.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "depth": {"type": "integer", "default": 1},
                },
                "required": ["path"],
            },
        },
    }

    for t in tools.TOOLS:
        nome = t.__name__
        if nome in tool_defs:
            tool_list.append(Tool(
                name=nome,
                description=tool_defs[nome]["description"],
                inputSchema=tool_defs[nome]["inputSchema"],
            ))
    return tool_list


# ============================================================
# EXECUTAR TOOL
# ============================================================
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    log.info(f"Tool chamada: {name} com {arguments}")

    # Encontrar a função
    func = None
    for t in tools.TOOLS:
        if t.__name__ == name:
            func = t
            break

    if not func:
        return [TextContent(type="text", text=f"Tool desconhecida: {name}")]

    try:
        resultado = func(**arguments)
        return [TextContent(type="text", text=resultado)]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro: {e}")]


# ============================================================
# MAIN
# ============================================================
async def main():
    log.info("MCP Server Everything a iniciar...")
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
