# Validacao de Atos Processuais e Cadeias CPC

**Autoridade**: [Backend/pydantic-ai/src/models_org.py](file:///c:/Users/Yokozuna/Dev/Backend/pydantic-ai/src/models_org.py)

---

## 1. Regras de Validacao de Cadeia Processual

1. **Dependencia de Citacao / Notificacao**:
   - Uma `CONTESTACAO` ou `OPOSICAO` exige a existencia previa de `CITACAO` ou `NOTIFICACAO`.
   - Se uma penhora ou despacho decisorio ocorrer sem citacao pregressa, o validador assinala `lacuna_detetada: true` (art. 188.º do CPC).

2. **Cadeia Recursal**:
   - Um `RECURSO` so pode ser admitido se existir uma `SENTENCA` ou `DESPACHO` recorrido na cadeia temporal.

3. **Validade de Prova**:
   - Qualquer ato qualificado como `DOCUMENTADO` exige obrigatoriamente hash `sha256` calculado ou referencia valida Citius.
