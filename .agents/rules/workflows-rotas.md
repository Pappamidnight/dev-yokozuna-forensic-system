# Regras de Rotas e Workflows de Agentes

**Autoridade**: [AI/skills/mcp-fs-pydantic-org/assets/routes_map.json](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/assets/routes_map.json)

---

## 1. Conexao de Rotas do Ecossistema

1. **Acervo Canonico (6 Pastas)**:
   - `00_Indice_E_MOCs` $\rightarrow$ Mapeamento global de 123.133+ ficheiros.
   - `01_PDFs_Oficiais` $\rightarrow$ Atos formais, despachos judiciais e autos (imutaveis, SHA-256).
   - `02_Minutas_E_Rascunhos` $\rightarrow$ Notas preparatorias e transcricoes (nunca despacho).
   - `03_Contratos_E_Acordos` $\rightarrow$ Instrumentos contratuais e fluxos financeiros.
   - `04_Processos_E_Pecas_Escritas` $\rightarrow$ Pecas judiciais completas e prazos CPC.
   - `05_Correspondencia_E_Comunicacoes` $\rightarrow$ Emails e cartas com comprovativo de entrega.
   - `_index` $\rightarrow$ Area autorizada para geracao de relatorios e JSONL (`auto_safe=True`).

2. **Estagios de Processamento**:
   - `01_INICIAL` $\rightarrow$ Peticoes iniciais e requerimentos executivos.
   - `02_CONTESTACAO` $\rightarrow$ Oposicoes e contestacoes.
   - `03_PROVAS` $\rightarrow$ Documentos fisicos, faturas e certidoes.
   - `04_ALEGACOES` $\rightarrow$ Articulados e alegacoes de direito.
   - `05_SENTENCA` $\rightarrow$ Decisoes judiciais, despachos saneadores e acordaos.
   - `06_RECURSOS` $\rightarrow$ Recursos para Tribunal da Relacao e Supremo Tribunal de Justica.

3. **Motor Forense (`Projects/blindada-agent`)**:
   - Processos ativos: `3719/25.0T8LSB`, `10153/24.7T8LSB`, `23142/22.7T8LSB`, `15547/26.0T8LSB`.
   - Modos de operacao: `writes_allowed: sandbox_only`.

---

## 2. Automatizacao e Watchdog

- O servico `watchdog_indexer.py` monitoriza continuamente o diretorio `Dev/`.
- Novos ficheiros sao indexados automaticamente com hash SHA-256 e qualificacao de ato CPC.
- O ficheiro [tree_dirs.md](file:///c:/Users/Yokozuna/Dev/tree_dirs.md) e mantido como referencia atualizada da hierarquia do projeto.
