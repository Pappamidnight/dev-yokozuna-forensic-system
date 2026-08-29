#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
estruturar_arquitetura_4_mundos.py - Estruturador e Orquestrador da Arquitetura em 4 Mundos Independentes.
Separa rigorosamente:
  01_RECURSOS_ORIGINAIS (Imutaveis / Protegidos)
  02_MOTOR_FORENSE (Codigo / Agentes / CORE-5 / Regras)
  03_RESULTADOS (Outputs Regeneraveis / Relatorios / Pecas)
  04_CONTROLO_E_INDICES (Indices / Workflows / Versoes / Decisoes)
Zero emojis conforme PROTOCOL.md e AGENTS.md.
"""

import os
import sys
import shutil
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")

DIR_01 = DEV_ROOT / "01_RECURSOS_ORIGINAIS"
DIR_02 = DEV_ROOT / "02_MOTOR_FORENSE"
DIR_03 = DEV_ROOT / "03_RESULTADOS"
DIR_04 = DEV_ROOT / "04_CONTROLO_E_INDICES"

SUBDIRS_01 = [
    "00_ENTRADA_POR_TRIAR",
    "01_CITIUS_TRIBUNAL",
    "02_CONTRATOS_ACORDOS",
    "03_PROVAS_FINANCEIRAS",
    "04_COMUNICACOES",
    "05_IMAGENS_VIDEO_AUDIO",
    "06_DOCUMENTOS_PESSOAIS",
    "99_QUARENTENA_DUPLICADOS"
]

SUBDIRS_02 = [
    "00_REGRAS",
    "01_WORKFLOWS",
    "02_INGESTAO",
    "03_HASHING_CUSTODIA",
    "04_CLASSIFICACAO",
    "05_CONFRONTO_4_CAMADAS",
    "06_THINK_TANK",
    "07_GERADORES",
    "08_VALIDADORES",
    "09_INTERFACES",
    "10_CORE5_SUPER_MOTOR",
    "VERSOES"
]

SUBDIRS_03 = [
    "00_ESTADO_DO_SISTEMA",
    "01_INDICES_E_RELATORIOS",
    "02_DADOS_ESTRUTURADOS",
    "03_LOGS_AUDITORIA",
    "04_PECAS_PROCESSUAIS",
    "05_PDFS_FINAIS",
    "06_DASHBOARDS_HTML",
    "07_DOSSIERS_ZIP",
    "08_MATRIZES_CONFRONTO",
    "09_COMUNIDADE_IMPACTO",
    "VERSOES"
]

def criar_pastas():
    print("=" * 80)
    print(" ESTRUTURACAO DA ARQUITETURA EM 4 MUNDOS INDEPENDENTES")
    print("=" * 80)

    # 1. Recursos Originais
    for sub in SUBDIRS_01:
        (DIR_01 / sub).mkdir(parents=True, exist_ok=True)
    print(f"[+] 01_RECURSOS_ORIGINAIS estruturado ({len(SUBDIRS_01)} subpastas)")

    # 2. Motor Forense
    for sub in SUBDIRS_02:
        (DIR_02 / sub).mkdir(parents=True, exist_ok=True)
    print(f"[+] 02_MOTOR_FORENSE estruturado ({len(SUBDIRS_02)} subpastas)")

    # 3. Resultados
    for sub in SUBDIRS_03:
        (DIR_03 / sub).mkdir(parents=True, exist_ok=True)
    print(f"[+] 03_RESULTADOS estruturado ({len(SUBDIRS_03)} subpastas)")

    # 4. Controlo e Indices
    DIR_04.mkdir(parents=True, exist_ok=True)
    print(f"[+] 04_CONTROLO_E_INDICES estruturado")

def sincronizar_conteudo_existente():
    print("\n[*] A sincronizar e migrar ficheiros estrategicos para os novos caminhos...")

    # Sincronizar Regras para 02_MOTOR_FORENSE/00_REGRAS
    regras_origem = [
        DEV_ROOT / "PROTOCOL.md",
        DEV_ROOT / "AGENTS.md",
        DEV_ROOT / "AI" / "INSTRUCOES_DETERMINISTICAS_MOTOR_IA.md",
        DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS" / "MANUAL_ESTILO_E_LAYOUT_UNIFORMIZADO.md"
    ]
    for r in regras_origem:
        if r.exists():
            shutil.copy2(r, DIR_02 / "00_REGRAS" / r.name)

    # Sincronizar CORE-5 para 02_MOTOR_FORENSE/10_CORE5_SUPER_MOTOR
    core5_origem = DEV_ROOT / "AI" / "core5"
    if core5_origem.exists():
        for f in core5_origem.glob("*"):
            if f.is_file():
                shutil.copy2(f, DIR_02 / "10_CORE5_SUPER_MOTOR" / f.name)

    # Sincronizar Ingestor, Think Tank e Orquestrador
    shutil.copy2(DEV_ROOT / "AI" / "ingestor" / "ai_forensic_ingestor.py", DIR_02 / "02_INGESTAO" / "ai_forensic_ingestor.py")
    shutil.copy2(DEV_ROOT / "AI" / "think_tank" / "ai_think_tank_engine.py", DIR_02 / "06_THINK_TANK" / "ai_think_tank_engine.py")
    shutil.copy2(DEV_ROOT / "AI" / "ai_master_orchestrator.py", DIR_02 / "01_WORKFLOWS" / "ai_master_orchestrator.py")

    # Sincronizar Motores Backend
    shutil.copy2(DEV_ROOT / "Backend" / "motor_confronto_lado_a_lado.py", DIR_02 / "05_CONFRONTO_4_CAMADAS" / "motor_confronto_lado_a_lado.py")
    shutil.copy2(DEV_ROOT / "Backend" / "gerar_layout_uniformizado.py", DIR_02 / "07_GERADORES" / "gerar_layout_uniformizado.py")
    shutil.copy2(DEV_ROOT / "Backend" / "scanner_irregularidades_forenses.py", DIR_02 / "08_VALIDADORES" / "scanner_irregularidades_forenses.py")
    shutil.copy2(DEV_ROOT / "Backend" / "ajax_forensic_server.py", DIR_02 / "09_INTERFACES" / "ajax_forensic_server.py")

    # Sincronizar Resultados de OUTPUT_CENTRALIZADO para 03_RESULTADOS
    out_dir = DEV_ROOT / "OUTPUT_CENTRALIZADO"
    if out_dir.exists():
        for item in out_dir.iterdir():
            if item.is_dir():
                dest = DIR_03 / item.name
                if not dest.exists():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
            elif item.is_file():
                shutil.copy2(item, DIR_03 / "01_INDICES_E_RELATORIOS" / item.name)

    print("[+] Sincronizacao de modulos e outputs concluida.")

def gerar_arquivos_de_controlo():
    print("\n[*] A gerar os 7 Ficheiros de Controlo e Indices...")

    # 1. MAPA_GERAL.md
    mapa_content = """# MAPA GERAL DA ARQUITETURA FORENSE (4 MUNDOS INDEPENDENTES)

**Versão Canónica**: 4.0.0 — Padrão Dev Yokozuna  
**Data**: 2026-08-29  
**Autoridade**: PROTOCOL.md e AGENTS.md

---

## ESTRUTURA GLOBAL E FLUXO UNIDIRECIONAL

```
┌───────────────────────────────┐
│   01_RECURSOS_ORIGINAIS       │  (Documentos Reais, Imutáveis, Read-Only, SHA-256)
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   02_MOTOR_FORENSE            │  (Código, Agentes, Workflows, Regras, CORE-5)
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   03_RESULTADOS               │  (Outputs Regeneráveis, Relatórios, Peças, PDFs)
└───────────────────────────────┘

        ▲
        │  (Governação e Navegação)
┌───────┴───────────────────────┐
│   04_CONTROLO_E_INDICES       │  (Mapa Geral, Índices, Workflows, Versões, Decisões)
└───────────────────────────────┘
```

---

## TABELA DE CORRESPONDÊNCIA E NAVEGAÇÃO

| Diretório | Função | Regra Operacional |
|---|---|---|
| [`01_RECURSOS_ORIGINAIS/`](file:///C:/Users/Yokozuna/Dev/01_RECURSOS_ORIGINAIS/) | Custódia e Arquivo de Provas | **NUNCA EDITAR**. Ficheiros são imutáveis e auditados por SHA-256. |
| [`02_MOTOR_FORENSE/`](file:///C:/Users/Yokozuna/Dev/02_MOTOR_FORENSE/) | Inteligência e Orquestração | Código e agentes versionados. Não armazena provas originais nem resultados finais. |
| [`03_RESULTADOS/`](file:///C:/Users/Yokozuna/Dev/03_RESULTADOS/) | Produção e Entrega | Ficheiros regeneráveis pelo motor a qualquer momento. |
| [`04_CONTROLO_E_INDICES/`](file:///C:/Users/Yokozuna/Dev/04_CONTROLO_E_INDICES/) | Gestão e Decisão | Responde a onde está cada coisa, que versões existem e qual workflow executar. |
"""
    with open(DIR_04 / "MAPA_GERAL.md", "w", encoding="utf-8") as f:
        f.write(mapa_content)

    # 2. INDICE_RECURSOS.md
    with open(DIR_04 / "INDICE_RECURSOS.md", "w", encoding="utf-8") as f:
        f.write("""# ÍNDICE GERAL DE RECURSOS ORIGINAIS (CUSTÓDIA E ARQUIVO)

1. `00_ENTRADA_POR_TRIAR/`: Ficheiros recebidos pendentes de triagem e cálculo de hash.
2. `01_CITIUS_TRIBUNAL/`: Atos judiciais formais, citações, notificações e despachos do Citius.
3. `02_CONTRATOS_ACORDOS/`: Contratos de arrendamento, adendas, confissões de dívida e termos notariais.
4. `03_PROVAS_FINANCEIRAS/`: Faturas (Fatura 1000002), extratos bancários, IES, balanços e relatórios TPA Unicre.
5. `04_COMUNICACOES/`: Transcrições de mensagens WhatsApp (2021-2022), emails e cartas registadas.
6. `05_IMAGENS_VIDEO_AUDIO/`: 12 vídeos de vistoria técnica (24/05/2024), 350+ fotos EXIF e áudios.
7. `06_DOCUMENTOS_PESSOAIS/`: Cadernetas prediais históricas, identificação pessoal e certidões fiscais.
8. `99_QUARENTENA_DUPLICADOS/`: Ficheiros duplicados isolados por hash idêntico.
""")

    # 3. INDICE_MOTOR.md
    with open(DIR_04 / "INDICE_MOTOR.md", "w", encoding="utf-8") as f:
        f.write("""# ÍNDICE DOS MOTORES FORENSES E MÓDULOS (02_MOTOR_FORENSE)

- **`00_REGRAS/`**: `PROTOCOL.md`, `AGENTS.md` e `MANUAL_ESTILO_E_LAYOUT_UNIFORMIZADO.md`.
- **`01_WORKFLOWS/`**: Orquestrador mestre `ai_master_orchestrator.py` (Sequência T0-T8).
- **`02_INGESTAO/`**: `ai_forensic_ingestor.py` (Ingestão universal de novos documentos).
- **`03_HASHING_CUSTODIA/`**: `pdf_identifier_tool.py` e validadores de integridade SHA-256.
- **`04_CLASSIFICACAO/`**: Classificadores determinísticos de precedência probatória.
- **`05_CONFRONTO_4_CAMADAS/`**: `motor_confronto_lado_a_lado.py` (Ato Oficial x Prova x Lei x Conclusão).
- **`06_THINK_TANK/`**: `ai_think_tank_engine.py` (Debate e consenso dos 6 agentes canónicos).
- **`07_GERADORES/`**: `gerar_layout_uniformizado.py` (Gerador de DOCX LibreOffice e PDF).
- **`08_VALIDADORES/`**: `scanner_irregularidades_forenses.py` e testes de conformidade 100/100.
- **`09_INTERFACES/`**: `ajax_forensic_server.py` (Servidor Web na porta 8088).
- **`10_CORE5_SUPER_MOTOR/`**: `motor_super_forense_core.py` (Orquestrador inteligente dos 10 micro-módulos).
""")

    # 4. INDICE_RESULTADOS.md
    with open(DIR_04 / "INDICE_RESULTADOS.md", "w", encoding="utf-8") as f:
        f.write("""# ÍNDICE DE RESULTADOS E ENTREGÁVEIS (03_RESULTADOS)

- **`01_INDICES_E_RELATORIOS/`**: Relatórios consolidados, compêndios Citius e sínteses periciais.
- **`02_DADOS_ESTRUTURADOS/`**: `TABELA_MESTRA_REFERENCIA_FORENSE.csv` e bases SQLite unificadas.
- **`04_PECAS_PROCESSUAIS/`**: Minutas de Contestação, Reconvenção e Reclamações CAAJ.
- **`05_PDFS_FINAIS/`**: Peças em PDF A4 de alta qualidade prontas para impressão e envio ao Tribunal.
- **`06_DASHBOARDS_HTML/`**: Dashboards visuais interativos lado a lado e galerias de provas.
- **`07_DOSSIERS_ZIP/`**: Pacotes comprimidos completos para arquivo e envio.
""")

    # 5. WORKFLOWS.md
    with open(DIR_04 / "WORKFLOWS.md", "w", encoding="utf-8") as f:
        f.write("""# GUIA OPERACIONAL DE WORKFLOWS FORENSES

1. **Workflow de Ingestão e Custódia**:
   - `01_RECURSOS_ORIGINAIS` -> `02_MOTOR_FORENSE/02_INGESTAO` -> Atualiza SQLite e hashes SHA-256.
2. **Workflow de Think Tank e Refinamento**:
   - Executa os 6 agentes canónicos e produz a síntese consensual de 100/100.
3. **Workflow de Confronto Lado a Lado**:
   - Confronta atos oficiais com provas materiais e gera o dashboard HTML e PDF.
4. **Workflow de Geração de Peças Judiciais**:
   - Gera minutas em formato DOCX (LibreOffice) e PDF no Layout Canónico Uniformizado.
""")

    # 6. VERSOES.md
    with open(DIR_04 / "VERSOES.md", "w", encoding="utf-8") as f:
        f.write("""# HISTÓRICO DE VERSÕES DO SISTEMA

- **v4.0.0 (2026-08-29)**: Estruturação em 4 Mundos Independentes (Recursos, Motor, Resultados, Controlo).
- **v3.0.0 (2026-08-28)**: Implementação do CORE-5 Forense (10 Micro-Módulos e 8 Tabelas Fortes).
- **v2.1.0 (2026-08-28)**: Criação da Tabela Mestra CSV de Conflito Zero e Layout Canónico Uniformizado.
- **v1.0.0 (2026-08-21)**: Início da custódia e auditoria dos 2.330 ficheiros do Tribunal.
""")

    # 7. DECISOES.md
    with open(DIR_04 / "DECISOES.md", "w", encoding="utf-8") as f:
        f.write("""# REGISTO DE DECISÕES ARQUITETURAIS E ESTRATÉGICAS

1. **Decisão 01**: Proibição total e absoluta de emojis em todo o código, logs e documentos oficiais.
2. **Decisão 02**: Tom estritamente sóbrio, institucional e documental (Score 100/100).
3. **Decisão 03**: Imutabilidade absoluta da pasta `01_RECURSOS_ORIGINAIS/` (Read-Only).
4. **Decisão 04**: Resultados em `03_RESULTADOS/` são sempre regeneráveis e descartáveis.
5. **Decisão 05**: O motor nunca alucina: o que não tiver suporte de prova é marcado como `necessita_validacao`.
""")

    print("[+] 7 Ficheiros de controlo gerados em 04_CONTROLO_E_INDICES.")

if __name__ == "__main__":
    criar_pastas()
    sincronizar_conteudo_existente()
    gerar_arquivos_de_controlo()
    print("\n" + "=" * 80)
    print(" ARQUITETURA EM 4 MUNDOS INDEPENDENTES CONCLUIDA COM SUCESSO!")
    print("=" * 80)
