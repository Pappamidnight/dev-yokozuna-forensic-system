# Guia Pericial: Utilização de The Sleuth Kit (TSK) e Autopsy no Acervo Forense

**Data**: 2026-08-28  
**Autoridade**: Sistema Forense Dev Yokozuna  
**Ferramentas Integradas**: The Sleuth Kit (TSK) & Autopsy Forensic Platform  
**Objetivo**: Auditoria profunda, recuperação de ficheiros apagados, linha temporal e extração de metadados

---

## 1. O Que o The Sleuth Kit e Autopsy Permitem Fazer

Com o **Autopsy** e o **The Sleuth Kit (TSK)** instalados na sua máquina, dispõe do mesmo padrão de investigação utilizado pela **Polícia Judiciária, FBI e tribunais internacionais**:

```
                       ARQUITETURA DE INVESTIGAÇÃO AUTOPSY & TSK
                                           │
         ┌───────────────────┬─────────────┴─────────────┬───────────────────┐
         │                   │                           │                   │
         ▼                   ▼                           ▼                   ▼
┌──────────────────┐┌──────────────────┐        ┌──────────────────┐┌──────────────────┐
│ CARVING DE DADOS ││ TIMELINE & EXIF  │        │ COMUNICAÇÕES     ││ HASH MATCHING    │
│ Recuperação de   ││ Análise temporal │        │ Mensagens, emails││ Cruzamento de    │
│ ficheiros apaga- ││ e metadados de   │        │ e anexos de chats││ hashes SHA-256 e │
│ dos nos discos   ││ fotos Samsung    │        │ WhatsApp/Outlook ││ deteção de alter│
└──────────────────┘└──────────────────┘        └──────────────────┘└──────────────────┘
```

---

## 2. Como Abrir e Analisar o Caso no Autopsy

1. Abra o **Autopsy** no seu computador.
2. Clique em **"New Case"** (Novo Caso):
   - **Case Name**: `DEV_YOKOZUNA_FORENSIC`
   - **Base Directory**: `C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\03_AUTOPSY_CASES`
3. Adicionar Fontes de Dados (**Add Data Source**):
   - Escolha **"Logical Files / Local Disk"**.
   - Selecione as pastas centrais:
     - `C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos`
     - `C:\Users\Yokozuna\OneDrive\GESTAO`
     - `F:\` (Discos externos de 2018, 2019 e 2022)
     - `I:\` e `J:\`
4. Módulos de Ingestão Recomendados a Ativar:
   - [CONFORME]  **Recent Activity** (histórico e downloads)
   - [CONFORME]  **Keyword Search** (pesquisa de termos como *Varela, Luísa Santos, 82K, Teresa, Unicre*)
   - [CONFORME]  **Email Parser & Communications** (leitura de ficheiros `.eml`, `.msg`, `.txt`)
   - [CONFORME]  **Picture & Video Analyzer (EXIF)** (extração de datas/horas de fotos e vídeos de vistoria)
   - [CONFORME]  **Hash Lookup** (utilizando o nosso manifesto `SHA256SUMS.txt` gerado).

---

## 3. Comandos Úteis do The Sleuth Kit (Linha de Comandos)

Se preferir usar o terminal TSK diretamente:

- **Listar ficheiros e pastas de uma partição (incluindo apagados)**:
  ```bash
  fls -r -d \\.\PhysicalDrive0
  ```
- **Recuperar todos os ficheiros apagados para uma pasta**:
  ```bash
  tsk_recover -e E:\ C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\recuperados_tsk\
  ```
- **Extrair texto e strings de setores não alocados**:
  ```bash
  srch_strings -a E:\ > C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\strings_extraidas.txt
  ```

---

## 4. Lançador Rápido de Integração

Criámos o inicializador no seu ambiente:
[ITEM]  [`EXECUTAR_SLEUTHKIT_AUTOPSY.bat`](file:///C:/Users/Yokozuna/Dev/EXECUTAR_SLEUTHKIT_AUTOPSY.bat)
