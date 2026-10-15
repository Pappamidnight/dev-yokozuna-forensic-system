# Arquitetura do Sistema: Acervo Forense V8

**Versao**: 8.0.0 Canónica  
**Data**: 2026-10-15  
**Ambiente**: Windows 11 Host (`C:\ACERVO`) / Rust 1.80+ / Python 3.12 (`uv`) / WSL2 Kali & Ubuntu  

---

## 1. Visao Estrutural de Alto Nivel

O sistema e desenhado como uma arquitetura desacoplada em tres camadas complementares:
1. **Camada de Ingestao e Indexacao**: Everything HTTP Engine e Everything SDK nativo.
2. **Camada de Processamento e Deduplicacao Atomica**: Python V8 Polars Engine e Crates Rust (`acervo_core`, `acervo_db`, `acervo_storage`, `acervo_search`).
3. **Camada de Prova, Metadados e Defesa Juridica**: Schemas Pydantic, Modelos YAML de Evidencia e Compilador Processual Markdown.

```
                      +------------------------------------------+
                      |       CLIENTES / CLI / OPERADOR          |
                      |   (main.py / executar_acervo.bat / MCP)  |
                      +--------------------+---------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
       +-------------------------+                   +-------------------------+
       |   EVERYTHING HTTP API   |                   |    CRATES RUST CORE     |
       |  (Porta 8080 - REST)    |                   |   (acervo_core/files)   |
       +------------+------------+                   +------------+------------+
                    |                                             |
                    v                                             v
       +-------------------------+                   +-------------------------+
       | MOTOR PYTHON V8 ATOMICO |                   |   ARMAZENAMENTO SEGURO  |
       | (Deduplicacao 1 Tipo)   |<----------------->|  - db/schema.sql        |
       +------------+------------+                   |  - storage/ (CAS blobs) |
                    |                                |  - reports/ (Manifests) |
                    v                                +-------------------------+
       +-------------------------+
       | CASO 15547 / PROVAS     |
       | - Refutacoes Cabais     |
       | - Dossiers de Defesa    |
       +-------------------------+
```

---

## 2. Componentes e Responsabilidades

### 2.1. Crates Rust (`crates/` e `services/`)
- `acervo_core`: Estruturas fundamentais de entidades, tipos MIME, hashing SHA-256 de alto debito e regras de conservacao.
- `acervo_db`: Camada de persistencia SQLite assincrona para indexacao transacional de ficheiros e eventos.
- `acervo_storage`: Modulo de Content-Addressable Storage (CAS) baseado no digest criptografico.
- `acervo_search`: Interface de pesquisa de metadados integrada ao Everything.
- `acervo_gateway`: Daemon de coordenacao de eventos em tempo real.

### 2.2. Motor Python V8 (`main.py` e `scripts/`)
- **CLI Atómica**: Fornece subcomandos unificados (`dedupe`, `scan`, `deploy-bat`, `status`).
- **Segregacao de Ficheiros**:
  - `originais_<tipo>.csv`: Ficheiros eleitos como matrizes canonicas com base no algoritmo de antiguidade e integridade.
  - `duplicados_<tipo>.csv`: Réplicas identificadas, mapeadas diretamente ao original eleito.
  - `manifesto_<tipo>.json`: Auditoria completa contendo contagens, tempos e byte-count recuperavel.

### 2.3. Model Context Protocol (MCP) (`mcp_everything/`)
- Exposição de ferramentas de busca forense, filtros por extensao, pesquisa regex e consultas semanticas para agentes de inteligencia artificial.

---

## 3. Topologia de Armazenamento e Diretórios

| Diretorio | Natureza | Politica de Acesso |
|---|---|---|
| `c:\ACERVO\bin\` | Binarios SDK nativos Everything | Read-Only |
| `c:\ACERVO\caso_15547\` | Pecas juridicas e mapas de defesa | Versionado (Git) |
| `c:\ACERVO\crates\` | Codigo-fonte Rust do motor de sistema | Versionado (Git) |
| `c:\ACERVO\db\` | Schema DDL relacional | Versionado (`schema.sql`) |
| `c:\ACERVO\gestao_provas\` | Schemas JSON e provas estruturadas YAML | Versionado (Git) |
| `c:\ACERVO\reports\` | Manifestos JSON e relatorios HTML | Versionado |
| `c:\ACERVO\scripts\` | Scripts forenses e pipelines analiticos | Versionado (Git) |
| `c:\ACERVO\storage\` | Blobs de ficheiros (Content-Addressable) | Git-Ignored / Imutavel |
| `c:\ACERVO\logs\` | Registos de execucao e snapshots | Git-Ignored / Volatil |
| `c:\ACERVO\00_ALTAR...` | Memorias protegidas (familia e animais) | Git-Ignored / Imutavel |

---

## 4. Pipeline de Processamento de Prova

```
[Pesquisa Everything HTTP]
          |
          v
[Extracao de Metadados: Path, Size, MTime]
          |
          v
[Calculo Criptografico SHA-256 sob Try/Except]
          |
          v
[Agrupamento por Hash e Heuristica de Precedencia]
          |
     +----+----+
     |         |
     v         v
[Original]  [Duplicado]
     |         |
     +----+----+
          |
          v
[Geracao de Manifesto JSON e Persistencia em Reports]
```
