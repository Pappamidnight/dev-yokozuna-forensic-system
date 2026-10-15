# Memoria e Custodia de Dados: Acervo Forense V8

**Norma de Conformidade**: ISO/IEC 27037 (Evidence Collection & Preservation)  
**Versao**: 8.0.0 Canónica  
**Data**: 2026-10-15  

---

## 1. Principios da Custodia Probatoria

A memoria do sistema rege-se pelo principio inegociavel da imutabilidade e rastreabilidade total:
1. **Identificacao Unica**: Cada entidade probatoria e indexada pelo seu digest SHA-256 de 64 caracteres hexadecimais.
2. **Preservacao do Original**: Ficheiros de prova bruta (`00_PROVA_ORIGINAL`, `01_CITIUS_CONGELADO`, etc.) permanecem estritamente intactos no sistema de ficheiros com carimbo de tempo preservado.
3. **Auditabilidade Bidirecional**: Para cada alegação em peca processual existe um apontador exato para o documento material correspondente.

---

## 2. Estrutura Canónica de Evidencias (YAML/JSON Schema)

Cada elemento de prova catalogado em `gestao_provas/` respeita a estrutura formal validada por `prova_schema.json`:

```yaml
id: "PRV-001"
titulo: "Risco Iminente de Incendio e Obras de Seguranca"
data_facto: "2020-03-15"
processo_vinculado: "15547/26.0T8LSB"
classificacao_legal: "Direito de Retencao / Benfeitorias Necessarias (Art. 754 CC)"
ficheiro_origem:
  nome: "fatura_eletricidade_quadro.pdf"
  caminho_relativo: "provas/faturas/2020/fatura_eletricidade_quadro.pdf"
  tamanho_bytes: 345120
  sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
metadados_contextuais:
  autor: "Lisbon Experience Lda"
  destinatario: "Senhorios / Manuel Varela"
  tema: "Substituicao de quadro eletrico ardido em Carnide"
impacto_juridico:
  alegacao_refutada: "AL-03: Falta de manutencao imputada ao reu"
  artigo_lei: "Art. 754.º e Art. 1273.º do Codigo Civil"
```

---

## 3. Gestao do Historico de 10 Anos (2014-2024)

O acervo integra um historico continuo de uma decada de relacao contratual, operacional e financeira:
- **Comunicacoes e Notificacoes**: Emails de servico, minutas de acordo e convocatorias de reuniao.
- **Transacoes Financeiras**: Extratos de transferencias, pagamentos de rendas e despesas de manutencao do imovel.
- **Registos WhatsApp**: Capturas com transcricao sequencial atestando intervencoes tecnicas de urgencia, cortes de fornecimento e presenca continuada no imovel.

---

## 4. O Altar Sagrado de Memorias Pessoais

O diretorio `00_ALTAR_MEMORIAS_PROTEGIDAS_FAMILIA_E_ANIMAIS`:
- Constitui um cofre estanque de fotografias familiares e de animais de companhia.
- **Funcao Forense**: Alem do valor afetivo inestimavel, comprova materialmente a vivencia ininterrupta, cuidado continuado e ocupacao legitima desde 2018, refutando a tese de esbulho recente alegada pela contraparte.
- **Protecao**: Totalmente excluido do Git para resguardo da intimidade familiar, permanecendo integralmente selado em disco com tabela de hashes preservada em [caso_15547/docs/ALTAR_MEMORIAS_FAMILIA_E_ANIMAIS.md](file:///c:/ACERVO/caso_15547/docs/ALTAR_MEMORIAS_FAMILIA_E_ANIMAIS.md).
