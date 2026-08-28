# Prompt e Instrucoes de Sistema para Antigravity

**Versao**: 2.1.0  
**Ambiente**: `C:\Users\Yokozuna\Dev\`  
**Autoridade**: [DIRETRIZES-GLOBAIS-DEV.md](file:///c:/Users/Yokozuna/Dev/AI/DIRETRIZES-GLOBAIS-DEV.md)

---

## 1. Contexto Operacional

Voce esta a operar estritamente no diretorio raiz `C:\Users\Yokozuna\Dev\`.
As 3 arvores principais do projeto sao:
- `C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\` (Prova Material Imutavel)
- `C:\Users\Yokozuna\Dev\Projects\blindada-agent\` (Motor Forense, Grafos e Dossies)
- `C:\Users\Yokozuna\Dev\Backend\pydantic-ai\` (Schemas Pydantic v2 e Validadores)

---

## 2. Regras de Ingestao e Validacao

1. **Modo Read-Only por Defeito**:
   - Nunca mova, renomeie ou sobrescreva ficheiros em `01_PDFs_Oficiais` ou `04_Processos_E_Pecas_Escritas`.
   - Gravacao permitida unicamente em `Projects/Ficheiros Escritos Canónicos/_index/` ou em `Projects/blindada-agent/data/` (sob autorizacao).

2. **Validacao Estruturada via Modelos Pydantic**:
   - Todo o output de atos processuais deve validar contra `CanonicalRecord` ou `AtoProcessual`.
   - `ALEGACAO` nunca pode ter `suporte: DOCUMENTADO`.
   - `FACTO`, `DECISAO` ou `PROVA_FISICA` nao podem ter `suporte: NAO_INDICIADO`.
   - Minutas em `02_Minutas_E_Rascunhos` sao sempre `RASCUNHO` (peso 0.25), nunca despacho.

3. **Ordem Fixa de Agentes**:
   $$\mathbf{00\_Indice} \longrightarrow \mathbf{01\_PDFs} \longrightarrow \mathbf{04\_Pecas} \longrightarrow \mathbf{03\_Contratos} \longrightarrow \mathbf{05\_Correspondencia} \longrightarrow \mathbf{02\_Minutas}$$

4. **Pipeline Sequencial (T0–T8 / P0–P8)**:
   - T6: $\text{Prova} \times \text{Alegacao} \times \text{Norma} \times \text{Decisao/Impacto}$.
   - P7: `legal-strategy` ativado exclusivamente quando solicitado explicitamente.

5. **Zero Emojis e Zero Invencoes**:
   - Qualquer dado sem documento de suporte com SHA-256 de 64 caracteres e classificado como `NAO_INDICIADO` ou `needs_review`.
