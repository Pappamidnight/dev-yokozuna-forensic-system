# Agentes Canonicos - Especificacao e Pesos Probatorios

Este documento define os 6 agentes canonicos associados as pastas do acervo em `C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\`.

---

## 1. Tabela Comparativa de Agentes

| Pasta | Agente | Funcao Principal | Peso | Nivel de Prova | Precedencia |
|---|---|---|---|---|---|
| `00_Indice_E_MOCs` | `agente-indice-mocs` | Catalogo e mapas de conteudo | 0.70 | INDICE | 1.º a executar |
| `01_PDFs_Oficiais` | `agente-pdfs-oficiais` | Atos oficiais e calculo SHA-256 | **1.00** | OFICIAL | Vence minutas |
| `02_Minutas_E_Rascunhos` | `agente-minutas` | Anotacoes e transcricoes | 0.25 | BAIXA | Ultimo a executar |
| `03_Contratos_E_Acordos` | `agente-contratos` | Partes, valores e assinaturas | 0.95 | ALTA | Vence rascunho |
| `04_Processos_E_Pecas_Escritas` | `agente-pecas` | Pecas e cadeia procedimental CPC | 0.98 | OFICIAL | Vence minutas |
| `05_Correspondencia_E_Comunicacoes` | `agente-correspondencia` | Comunicacoes, canal e data/hora | 0.85 | MEDIA | FACTO $\neq$ ALEGACAO |

---

## 2. Definicao Detalhada de Cada Agente

### 2.1 `agente-indice-mocs`
- **Pasta**: `00_Indice_E_MOCs`
- **Atribuicoes**:
  - Leitura de `INDEX_MESTRE_FICHEIROS_ESCRITOS.md`.
  - Construcao de rotas de acesso rapido e sumarios de volume.
  - Alerta: Nao gera conclusoes juridicas de merito.

### 2.2 `agente-pdfs-oficiais`
- **Pasta**: `01_PDFs_Oficiais`
- **Atribuicoes**:
  - Extracao de texto de sentencas, despachos judiciais, notificacoes de AE, autos de penhora.
  - Calculo rigoroso de SHA-256 para cada ficheiro.
  - Atribuicao da tag `prova-documental-oficial`.

### 2.3 `agente-minutas`
- **Pasta**: `02_Minutas_E_Rascunhos`
- **Atribuicoes**:
  - Triagem de ideias, argumentos de defesa preliminares e comunicacoes informais.
  - Garantia de que nenhum apontamento seja tomado como ato transitado em julgado.

### 2.4 `agente-contratos`
- **Pasta**: `03_Contratos_E_Acordos`
- **Atribuicoes**:
  - Identificacao de contratos de arrendamento, transacoes e acordos comerciais.
  - Mapeamento de montantes, datas de vigencia, renovacoes e assinaturas.

### 2.5 `agente-pecas`
- **Pasta**: `04_Processos_E_Pecas_Escritas`
- **Atribuicoes**:
  - Leitura de articulados, oposicoes a penhora, recursos para Tribunal da Relacao.
  - Extracao de numeros de processo (ex: `3719/25.0T8LSB`, `10153/24.7T8LSB`).
  - Verificacao de prazos processuais e identificacao de nulidades formais.

### 2.6 `agente-correspondencia`
- **Pasta**: `05_Correspondencia_E_Comunicacoes`
- **Atribuicoes**:
  - Extracao de emails e cartas registadas.
  - Classificacao de mensagens como FACTO (com aviso de rececao) ou ALEGACAO (unilateral).
