# INGESTAO 15547

Backend local, sem frontend/GUI, para ingestao deterministica de evidencias do processo `15547/26.0T8LSB`.

## Principios

- `raw/` e tratado como fonte original. O pipeline apenas le ficheiros e calcula SHA-256.
- Nao inventa factos.
- Separa sempre `FACTO_DOCUMENTADO`, `ALEGACAO`, `INFERENCIA`, `TESE_DEFESA` e `POR_VALIDAR`.
- Mantem logs, indice de evidencias, cronologia, claims, lacunas e relatorio Markdown.

## Uso

1. Colocar exports, PDFs, TXT, MD, CSV ou JSON em `raw/`.
2. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

3. Executar:

```powershell
python ingestao.py
```

## Outputs

- `outputs/jsonl/evidencias.jsonl`
- `outputs/jsonl/claims.jsonl`
- `outputs/jsonl/cronologia.jsonl`
- `outputs/jsonl/lacunas.jsonl`
- `outputs/jsonl/rotas_workflow.jsonl`
- `outputs/graph/nodes.jsonl`
- `outputs/graph/edges.jsonl`
- `outputs/evals/frozen_judge_eval.json`
- `outputs/markdown/RELATORIO_15547.md`
- `logs/ingestao.log`
- `logs/errors.log`
- `state/manifest.json`

## Fabrica multi-agente por 15 minutos

Executar:

```powershell
.\start_fabrica_15min.bat
```

Durante 15 minutos o watchdog observa `raw/`. Sempre que houver alteracao, o pipeline e executado novamente. Depois dos 15 minutos, encerra.

## Agentes

- `WorkflowAgent`: prepara estrutura e garante operacao sem GUI.
- `FrozenJudgeAgent`: valida entrada e decide rotas do workflow.
- `ValidadeAgent`: rebaixa rotulos juridicos fortes para `POR_VALIDAR` quando necessario.
- `JudgeAuditorAgent`: confirma o Frozen Judge contra gold dataset/evals.
- `GraphifyAgent`: cria grafo de pessoas, locais, valores e claims.
- `ObservabilidadeAgent`: mantem logs operacionais e logs de erro separados.

## Tipos de fonte previstos

Textos, exports WhatsApp, Markdown, CSV, JSON, logs, PDFs, imagens, DOCX e emails sao indexados por hash. A extracao textual deterministica e imediata para ficheiros textuais. PDFs, imagens, DOCX e emails entram indexados e roteados para parser especializado/OCR/conversao sem alterar RAW.
