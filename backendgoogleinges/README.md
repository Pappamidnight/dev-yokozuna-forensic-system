# backendgoogleinges - Sincronização Google Cloud (Gmail & Google Drive)

Módulo autónomo para descarregar, auditar (SHA-256) e organizar localmente todos os processos judiciais, peças, provas e anexos guardados no Gmail e no Google Drive.

---

## 📂 Estrutura do Pacote

```
backendgoogleinges/
├── config/
│   ├── credentials.json       # O seu ficheiro OAuth Client ID do Google Cloud
│   ├── token.json             # Gerado automaticamente após a 1ª autorização
│   └── credentials_template.json
├── data/
│   └── raw/
│       ├── gmail/             # Emails (.md) e anexos (.pdf, .txt, etc.) por label
│       ├── gdrive/            # Ficheiros e pastas transferidos do Google Drive
│       └── _index/
│           └── GOOGLE_INGEST_MANIFEST.json # Registo auditável com hashes SHA-256
├── google_ingest.py           # Motor de ingestão e download
├── executar_ingestao_google.bat # Script de execução com duplo clique
├── requirements.txt           # Dependências
└── README.md
```

---

## ⚡ Como Configurar em 2 Passos

### 1. Criar credencial no Google Cloud Console
1. Aceda a [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials).
2. Certifique-se de que a **Gmail API** e a **Google Drive API** estão ativadas no seu projeto.
3. Clique em **Create Credentials** -> **OAuth Client ID**.
4. Selecione o tipo de aplicação: **Desktop App**.
5. Descarregue o ficheiro JSON e guarde-o como:
   `C:\Users\Yokozuna\Dev\backendgoogleinges\config\credentials.json`

### 2. Instalar Dependências e Executar
```bash
pip install -r requirements.txt
```

Para iniciar a transferência:
* **Opção 1:** Dê duplo clique em `executar_ingestao_google.bat`.
* **Opção 2:** Execute no terminal:
  ```bash
  python google_ingest.py
  ```

---

## 🎯 Labels e Pastas Pré-configuradas

* **Labels do Gmail:**
  - `3719/25.0T8LSB`
  - `ANALISTA`
  - `CENTENARIO`
  - `Finpartner`

* **Pastas da Google Drive:**
  - `1 TRIBUNAL`
  - `MAPA PROVAS`
  - `SPARK 2926`
  - `02 Assuntos Jurídicos Críticos: Foco total na documentação`
  - `01 Negócio/Projeto Principal: Estrutura, Processos, Ferramen`
  - `_KB`
