#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Motor Central de Orquestracao Forense e Conexao do Filesystem
Versao: 8.2.0 Enterprise Forense
Padroes: Six Sigma, Pydantic, NLP Forense, Doutrina V8 (Conservacao Matematica).
"""

import os
import sys
import csv
import json
import re
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Any

# ==============================================================================
# 1. INTEGRACAO PYDANTIC (COM FALLBACK RESILIENTE)
# ==============================================================================
try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        def model_dump(self):
            return self.dict()

    def Field(default=None, **kwargs):
        return default


class EntidadesForenses(BaseModel):
    processos: List[str] = Field(default_factory=list)
    nifs: List[str] = Field(default_factory=list)
    ibans: List[str] = Field(default_factory=list)
    valores_eur: List[str] = Field(default_factory=list)
    datas: List[str] = Field(default_factory=list)


class MetadadosFicheiro(BaseModel):
    caminho: str
    nome: str
    stem: str
    ext: str
    tipo: str
    tamanho_bytes: int
    data_modificacao: str
    profundidade: int
    contexto: str = "GERAL"
    entidades: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ManifestoConservacao(BaseModel):
    tipo: str
    timestamp: str
    estado: str
    total_analisado: int
    grupos_unicos: int
    originais_eleitos: int
    duplicados_identificados: int
    erros_io: int
    espaco_recuperavel_bytes: int
    espaco_recuperavel_humano: str
    tempo_execucao_segundos: float
    conservacao_cumprida: bool


# ==============================================================================
# 2. MOTOR DE CLASSIFICACAO E NLP FORENSE
# ==============================================================================
class NLPClassifier:
    """Classificador deterministico por regex e heuristica juridica."""

    RE_PROCESSO = re.compile(r"\b(\d{3,6}[/\.]\d{2}(?:\.\d)?[A-Z0-9]{3,7})\b", re.IGNORECASE)
    RE_NIF = re.compile(r"\b([1235689]\d{8})\b")
    RE_IBAN = re.compile(r"\b(PT50\s*(?:\d\s*){21})\b", re.IGNORECASE)
    RE_VALOR = re.compile(r"(?:€|EUR)\s*([0-9\.\,]+)|([0-9\.\,]+)\s*(?:€|EUR)", re.IGNORECASE)
    RE_DATA = re.compile(r"\b(20\d{2}[-_/]\d{1,2}[-_/]\d{1,2}|\d{1,2}[-_/]\d{1,2}[-_/]20\d{2})\b")

    PALAVRAS_CHAVE_CONTEXTO = {
        "OFICIAL_TRIBUNAL": ["notificacao", "citius", "sentenca", "despacho", "tribunal", "citacao"],
        "PECA_PROCESSUAL": ["peticao", "contestacao", "requerimento", "oposicao", "embargos"],
        "CONTRATO": ["contrato", "acordo", "arrendamento", "clausula", "outorgante"],
        "FINANCEIRO": ["fatura", "recibo", "retencao", "transferencia", "comprovativo", "banco", "saldo"],
        "COMUNICACAO": ["whatsapp", "email", "conversa", "chat", "mensagem"],
        "PERITAGEM": ["peritagem", "relatorio", "avaliacao", "orcamento", "obras"]
    }

    @classmethod
    def extrair_entidades(cls, texto: str) -> EntidadesForenses:
        processos = list(set(cls.RE_PROCESSO.findall(texto)))
        nifs = list(set(cls.RE_NIF.findall(texto)))
        ibans = list(set(re.sub(r"\s+", "", i) for i in cls.RE_IBAN.findall(texto)))

        valores_brutos = cls.RE_VALOR.findall(texto)
        valores = []
        for v1, v2 in valores_brutos:
            v = (v1 or v2).strip()
            if v and v not in valores:
                valores.append(v)

        datas = list(set(cls.RE_DATA.findall(texto)))

        return EntidadesForenses(
            processos=processos,
            nifs=nifs,
            ibans=ibans,
            valores_eur=valores,
            datas=datas
        )

    @classmethod
    def classificar_contexto(cls, nome_ou_caminho: str) -> str:
        s = nome_ou_caminho.lower()
        for ctx, termos in cls.PALAVRAS_CHAVE_CONTEXTO.items():
            if any(t in s for t in termos):
                return ctx
        return "DOCUMENTO_GERAL"


# ==============================================================================
# 3. CONFIGURACOES E REGRAS DE FILESYSTEM
# ==============================================================================
MAPA_EXTENSOES = {
    "pdf": {".pdf"},
    "imagem": {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg", ".aac", ".opus", ".flac", ".wma"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
    "excel": {".xlsx", ".xls", ".ods", ".csv"},
    "word": {".docx", ".doc", ".odt"},
    "database": {".sqlite", ".sqlite3", ".db", ".duckdb"}
}

PASTAS_PROVA_CANONICAS = [
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_15547"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_3719"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_10153"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_20203"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_23142"),
    Path(r"C:\Users\Yokozuna\Desktop\DOSSIER_15547"),
    Path(r"C:\Users\Yokozuna\Desktop\PROJETO_15547"),
    Path(r"C:\Users\Yokozuna\Desktop\00_DOCUMENTOS_OFICIAIS_TRIBUNAL"),
    Path(r"C:\Users\Yokozuna\Desktop\RECUPERADOS_JURIDICO"),
    Path(r"C:\Users\Yokozuna\Desktop\ACERVO_FORENSE"),
    Path(r"C:\Users\Yokozuna\Desktop\ACERVO_FINAL_ORGANIZADO"),
    Path(r"C:\Users\Yokozuna\Desktop\LEA"),
    Path(r"C:\Users\Yokozuna\Desktop\SPARK"),
    Path(r"C:\Users\Yokozuna\Desktop\whatsapp_backup"),
    Path(r"C:\ACERVO"),
]

PASTAS_IGNORAR = {
    ".git", ".venv", "node_modules", "__pycache__", "site-packages",
    "quarentena", "AppData", "$Recycle.Bin", "target", ".cargo"
}

SAIDA_REPORTS = Path(r"C:\ACERVO\reports")
SAIDA_LOGS = Path(r"C:\ACERVO\logs")
SAIDA_REPORTS.mkdir(parents=True, exist_ok=True)
SAIDA_LOGS.mkdir(parents=True, exist_ok=True)


def formatar_tamanho(bytes_total: int) -> str:
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_total < 1024:
            return f"{bytes_total:.2f} {u}"
        bytes_total /= 1024
    return f"{bytes_total:.2f} PB"


# ==============================================================================
# 4. MOTOR DE INVENTARIO E DEDUPLICACAO UNITARIA
# ==============================================================================
class MotorOrquestrador:

    @staticmethod
    def rastrear_tipo(tipo: str, pastas: Optional[List[Path]] = None) -> (List[MetadadosFicheiro], int):
        tipo = tipo.lower()
        if tipo not in MAPA_EXTENSOES:
            raise ValueError(f"Tipo invalido: '{tipo}'. Tipos permitidos: {list(MAPA_EXTENSOES.keys())}")

        extensoes_alvo = MAPA_EXTENSOES[tipo]
        alvos = pastas or PASTAS_PROVA_CANONICAS
        registos = []
        erros_io = 0

        for pasta in alvos:
            try:
                if not pasta.exists():
                    continue
            except (OSError, PermissionError):
                erros_io += 1
                continue

            try:
                for raiz, dirs, ficheiros in os.walk(pasta):
                    dirs[:] = [d for d in dirs if d not in PASTAS_IGNORAR]

                    for nome in ficheiros:
                        ext = Path(nome).suffix.lower()
                        if ext not in extensoes_alvo:
                            continue

                        caminho_completo = Path(raiz) / nome
                        try:
                            tam = caminho_completo.stat().st_size
                            if tam <= 0:
                                continue
                            mod_time = datetime.fromtimestamp(caminho_completo.stat().st_mtime).isoformat()
                        except OSError:
                            erros_io += 1
                            continue

                        # Extracao de entidades por NLP sobre o caminho e nome
                        entidades = NLPClassifier.extrair_entidades(str(caminho_completo))
                        contexto = NLPClassifier.classificar_contexto(str(caminho_completo))

                        meta = MetadadosFicheiro(
                            caminho=str(caminho_completo),
                            nome=nome,
                            stem=caminho_completo.stem.lower(),
                            ext=ext,
                            tipo=tipo,
                            tamanho_bytes=tam,
                            data_modificacao=mod_time,
                            profundidade=len(caminho_completo.parts),
                            contexto=contexto,
                            entidades=entidades.model_dump() if HAS_PYDANTIC else entidades.dict()
                        )
                        registos.append(meta)
            except OSError:
                erros_io += 1
                continue

        return registos, erros_io

    @staticmethod
    def rastrear_everything_http(tipo: str, porta: int = 8080) -> (List[MetadadosFicheiro], int):
        """Consulta o Everything 1.5 via HTTP na porta 8080 com fallback automatico."""
        import urllib.parse
        import urllib.request
        tipo = tipo.lower()
        if tipo not in MAPA_EXTENSOES:
            raise ValueError(f"Tipo invalido: '{tipo}'")

        extensoes_query = ";".join(e.lstrip(".") for e in MAPA_EXTENSOES[tipo])
        filtro = f'ext:{extensoes_query} <"C:\\Users\\Yokozuna\\Desktop" | "C:\\ACERVO"> !"site-packages" !".venv" !"node_modules" !"$Recycle.Bin" !"AppData"'
        params = urllib.parse.urlencode({
            "search": filtro,
            "json": "1",
            "count": "50000",
            "path_column": "1",
            "size_column": "1",
            "date_modified_column": "1"
        })
        url = f"http://127.0.0.1:{porta}/?{params}"
        registos = []
        erros = 0

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AGY-Forensic/8.2"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("results", []):
                    caminho_dir = item.get("path", "")
                    nome = item.get("name", "")
                    caminho = str(Path(caminho_dir) / nome)
                    try:
                        tam = int(item.get("size", 0))
                    except (ValueError, TypeError):
                        continue
                    if tam <= 0:
                        continue
                    ext = Path(nome).suffix.lower()
                    entidades = NLPClassifier.extrair_entidades(caminho)
                    contexto = NLPClassifier.classificar_contexto(caminho)
                    meta = MetadadosFicheiro(
                        caminho=caminho,
                        nome=nome,
                        stem=Path(nome).stem.lower(),
                        ext=ext,
                        tipo=tipo,
                        tamanho_bytes=tam,
                        data_modificacao=str(item.get("date_modified", "")),
                        profundidade=len(Path(caminho).parts),
                        contexto=contexto,
                        entidades=entidades.model_dump() if HAS_PYDANTIC else entidades.dict()
                    )
                    registos.append(meta)
            print(f"[HTTP 8080] Recuperados {len(registos):,} ficheiros do tipo [{tipo.upper()}] via Everything HTTP.")
            return registos, erros
        except Exception as e:
            print(f"[INFO HTTP] Everything HTTP falhou ({e}). A recorrer a varredura local...")
            return MotorOrquestrador.rastrear_tipo(tipo)

    @staticmethod
    def segregar_e_validar(tipo: str, registos: List[MetadadosFicheiro], erros_io: int, tempo_total: float):
        grupos = defaultdict(list)
        for r in registos:
            chave = (r.stem, r.tamanho_bytes, r.ext)
            grupos[chave].append(r)

        originais = []
        duplicados = []

        for chave, lista in grupos.items():
            if len(lista) == 1:
                originais.append(lista[0])
                continue

            # Prioridade de soberania: menor profundidade e caminho mais curto
            lista.sort(key=lambda x: (x.profundidade, len(x.caminho), x.caminho))
            originais.append(lista[0])

            original_path = lista[0].caminho
            for dup in lista[1:]:
                item_dup = dup.model_dump() if HAS_PYDANTIC else dup.dict()
                item_dup["original_eleito"] = original_path
                duplicados.append(item_dup)

        total_entrada = len(registos)
        total_saida = len(originais) + len(duplicados)
        diferenca = total_entrada - total_saida
        conservado = (diferenca == 0 and len(grupos) == len(originais))
        estado = "VALIDADO" if conservado else "FALHA_CONSERVACAO"

        espaco = sum(d["tamanho_bytes"] for d in duplicados)
        manifesto = ManifestoConservacao(
            tipo=tipo,
            timestamp=datetime.now().isoformat(),
            estado=estado,
            total_analisado=total_entrada,
            grupos_unicos=len(grupos),
            originais_eleitos=len(originais),
            duplicados_identificados=len(duplicados),
            erros_io=erros_io,
            espaco_recuperavel_bytes=espaco,
            espaco_recuperavel_humano=formatar_tamanho(espaco),
            tempo_execucao_segundos=round(tempo_total, 2),
            conservacao_cumprida=conservado
        )

        return originais, duplicados, manifesto

    @staticmethod
    def persistir_resultado(tipo: str, originais: list, duplicados: list, manifesto: ManifestoConservacao):
        # 1. CSV Originais
        path_orig = SAIDA_REPORTS / f"originais_{tipo}.csv"
        colunas = ["tipo", "nome", "stem", "ext", "tamanho_bytes", "caminho", "data_modificacao", "contexto"]
        with open(path_orig, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore")
            w.writeheader()
            for r in originais:
                d = r.model_dump() if HAS_PYDANTIC else r.dict()
                w.writerow(d)

        # 2. CSV Duplicados
        path_dup = SAIDA_REPORTS / f"duplicados_{tipo}.csv"
        colunas_dup = colunas + ["original_eleito"]
        with open(path_dup, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colunas_dup, extrasaction="ignore")
            w.writeheader()
            for d in duplicados:
                w.writerow(d)

        # 3. JSON Manifesto
        path_man = SAIDA_REPORTS / f"manifesto_{tipo}.json"
        with open(path_man, "w", encoding="utf-8") as f:
            data = manifesto.model_dump() if HAS_PYDANTIC else manifesto.dict()
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path_orig, path_dup, path_man


# ==============================================================================
# 5. GERADOR DE DEPLOY E FICHEIROS BATCH (.BAT)
# ==============================================================================
def gerar_deploy_bat(destino: Path = Path(r"C:\ACERVO\executar_acervo.bat")):
    """Gera script .bat de execucao direta no Windows para operador."""
    conteudo = r"""@echo off
chcp 65001 >nul
cls
echo ==============================================================================
echo   ACERVO FORENSE V8 — PAINEL DE DISPARO SEQUENCIAL (1 TIPO DE CADA VEZ)
echo ==============================================================================
echo.
echo [1] Executar Fase PDF      (P0 - Documentos Judiciais e Certidoes)
echo [2] Executar Fase Imagens  (P1 - Comprovativos, WhatsApp, Faturas)
echo [3] Executar Fase Audios   (P1 - Mensagens de Voz)
echo [4] Executar Fase Videos   (P2 - Videos de Obras e Diligencias)
echo [5] Executar Fase Excel    (P1 - Tabelas de Saldo e Despesas)
echo [6] Executar Fase Word     (P2 - Minutas e Articulados)
echo [7] Executar Todas as Fases Sequencialmente (Modo Auditoria)
echo [8] Ver Relatorios e Manifestos Gerados
echo [9] Sair
echo.
set /p opt="Escolha a opcao [1-9]: "

if "%opt%"=="1" (
    python C:\ACERVO\main.py dedupe --tipo pdf
    pause
    goto fim
)
if "%opt%"=="2" (
    python C:\ACERVO\main.py dedupe --tipo imagem
    pause
    goto fim
)
if "%opt%"=="3" (
    python C:\ACERVO\main.py dedupe --tipo audio
    pause
    goto fim
)
if "%opt%"=="4" (
    python C:\ACERVO\main.py dedupe --tipo video
    pause
    goto fim
)
if "%opt%"=="5" (
    python C:\ACERVO\main.py dedupe --tipo excel
    pause
    goto fim
)
if "%opt%"=="6" (
    python C:\ACERVO\main.py dedupe --tipo word
    pause
    goto fim
)
if "%opt%"=="7" (
    for %%t in (pdf imagem audio video excel word) do (
        echo.
        echo ==============================================================================
        echo A PROCESSAR TIPO: %%t
        echo ==============================================================================
        python C:\ACERVO\main.py dedupe --tipo %%t
    )
    pause
    goto fim
)
if "%opt%"=="8" (
    explorer C:\ACERVO\reports
    goto fim
)
:fim
exit /b 0
"""
    destino.write_text(conteudo, encoding="utf-8")
    return destino


# ==============================================================================
# 6. ENTRADA CLI PRINCIPAL
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Acervo Forense V8 — Motor Central de Orquestracao")
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponiveis")

    # Subcomando: dedupe
    p_dedupe = subparsers.add_parser("dedupe", help="Deduplica e valida 1 tipo especifico de cada vez")
    p_dedupe.add_argument("--tipo", required=True, choices=list(MAPA_EXTENSOES.keys()), help="Tipo a processar")

    # Subcomando: scan
    p_scan = subparsers.add_parser("scan", help="Rastreia e extrai entidades forenses")
    p_scan.add_argument("--tipo", default="pdf", choices=list(MAPA_EXTENSOES.keys()), help="Tipo a rastrear")

    # Subcomando: deploy-bat
    p_deploy = subparsers.add_parser("deploy-bat", help="Gera o ficheiro de execucao .bat")
    p_deploy.add_argument("--caminho", default=r"C:\ACERVO\executar_acervo.bat", help="Destino do .bat")

    # Subcomando: rust-ml
    p_rust = subparsers.add_parser("rust-ml", help="Executa o motor Rust de alta velocidade para extracao de features e hashing")
    p_rust.add_argument("--acao", choices=["hash", "features", "scan-features"], default="features", help="Acao a executar")
    p_rust.add_argument("--alvo", required=True, help="Ficheiro ou diretorio alvo")
    p_rust.add_argument("--saida", default=None, help="Caminho do ficheiro de saida (para scan-features)")

    # Subcomando: status
    subparsers.add_parser("status", help="Mostra o estado dos manifestos gerados")

    args = parser.parse_args()

    if args.comando == "rust-ml":
        import subprocess
        cmd = ["cargo", "run", "--manifest-path", r"C:\ACERVO\Cargo.toml", "-p", "acervo-forensic-ml", "--bin", "forensic-ml", "--", args.acao, args.alvo]
        if args.saida:
            cmd.append(args.saida)
        print(f"[RUST-ML] A executar: {' '.join(cmd)}")
        res = subprocess.run(cmd)
        return

    if not args.comando or args.comando == "status":
        print("=" * 78)
        print("  ESTADO ATUAL DO ACERVO FORENSE (C:\\ACERVO\\reports)")
        print("=" * 78)
        encontrados = list(SAIDA_REPORTS.glob("manifesto_*.json"))
        if not encontrados:
            print("  Nenhum manifesto gerado ainda. Execute 'python main.py dedupe --tipo pdf'.")
        else:
            for m in encontrados:
                try:
                    d = json.loads(m.read_text(encoding="utf-8"))
                    print(f"  Tipo: {d.get('tipo', '').upper():<10} | Estado: {d.get('estado', ''):<16} | Total: {d.get('total_analisado', 0):>6} | Duplicados: {d.get('duplicados_identificados', 0):>6}")
                except Exception:
                    pass
        print("=" * 78)
        return

    if args.comando == "deploy-bat":
        caminho_bat = Path(args.caminho)
        gerar_deploy_bat(caminho_bat)
        print(f"[OK] Ficheiro batch de execucao gerado em: {caminho_bat}")
        return

    if args.comando in ("dedupe", "scan"):
        tipo = args.tipo.lower()
        t0 = time.time()
        print("=" * 78)
        print(f"  ACERVO FORENSE V8 — PROCESSAMENTO ATOMICO: [{tipo.upper()}]")
        print("=" * 78)

        registos, erros_io = MotorOrquestrador.rastrear_everything_http(tipo)
        if not registos:
            print(f"[AVISO] Nenhum ficheiro do tipo '{tipo}' encontrado.")
            return

        t_total = time.time() - t0
        originais, duplicados, manifesto = MotorOrquestrador.segregar_e_validar(tipo, registos, erros_io, t_total)
        p_orig, p_dup, p_man = MotorOrquestrador.persistir_resultado(tipo, originais, duplicados, manifesto)

        print(f"  Total Analisado:       {manifesto.total_analisado:>8,}")
        print(f"  Originais Eleitos:     {manifesto.originais_eleitos:>8,}")
        print(f"  Duplicados Detetados:  {manifesto.duplicados_identificados:>8,}")
        print(f"  Espaco Redundante:     {manifesto.espaco_recuperavel_humano}")
        print(f"  Estado Conservacao:    {manifesto.estado}")
        print(f"  Tempo Total:           {manifesto.tempo_execucao_segundos:.2f}s")
        print("-" * 78)
        print(f"  Artefactos Gravados:")
        print(f"    - Originais:   {p_orig}")
        print(f"    - Duplicados:  {p_dup}")
        print(f"    - Manifesto:   {p_man}")
        print("=" * 78)


if __name__ == "__main__":
    main()
