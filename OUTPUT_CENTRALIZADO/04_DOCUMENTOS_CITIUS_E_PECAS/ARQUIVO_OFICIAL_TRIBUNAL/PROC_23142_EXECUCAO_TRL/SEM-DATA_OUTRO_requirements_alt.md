---
tipo: OUTRO
data: null
processo: 23142/22.7T8LSB + 33934
processo_nome: CENTENARIO
tribunal: null
fonte: documento-oficial
ficheiro: "requirements.txt"
extensao: .txt
tamanho_kb: 0.8
texto_extraido: true
caminho_original: "C:/Users/nunom/Desktop/CENTENARIOTRL\files (5)\requirements.txt"
tags:
  - tipo/outro
  - processo/centenario
---

# OUTRO -- requirements

**Tipo:** OUTRO
**Processo:** 23142/22.7T8LSB + 33934 (Execucao Centenario)
**Resumo:** # ═══════════════════════════════════════════════════════════════
**Ficheiro:** `requirements.txt` (0.8 KB)
**Origem:** `C:/Users/nunom/Desktop/CENTENARIOTRL\files (5)\requirements.txt`

> Voltar: [[_INDICE_CENTENARIO]] | [[HOME]]

## Conteudo

```
# ═══════════════════════════════════════════════════════════════
# MINMOP — Dependencies
# ═══════════════════════════════════════════════════════════════

# Core
pyyaml>=6.0
python-dateutil>=2.8

# NLP
spacy>=3.7
# After install: python -m spacy download pt_core_news_lg
langdetect>=1.0.9

# ML
scikit-learn>=1.4
numpy>=1.26

# Embeddings
sentence-transformers>=2.7

# Search
elasticsearch>=8.12

# Document extraction
PyMuPDF>=1.24       # PDF (import fitz)
pdfplumber>=0.11    # PDF fallback
python-docx>=1.1    # DOCX
beautifulsoup4>=4.12 # HTML
lxml>=5.1           # HTML parser

# Utilities
tqdm>=4.66
```
