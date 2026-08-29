# Como o Autopsy e The Sleuth Kit Criam Gráficos de Vínculos e Suportam Plugins Python

**Data**: 2026-08-28  
**Autoridade**: Sistema Forense Dev Yokozuna  
**Ambiente**: Autopsy Forensic Browser & The Sleuth Kit (TSK)

---

## 1. Sim! O Autopsy Tem Gráfico Visual de Comunicações e Vínculos

O Autopsy possui uma ferramenta nativa avançada chamada **"Communications Visualization"** (Gráfico de Vínculos de Comunicação):

```
                       PAINEL COMMUNICATIONS GRAPH DO AUTOPSY
                                          │
         ┌────────────────────────────────┴────────────────────────────────┐
         ▼                                                                 ▼
┌──────────────────────────────────────┐                  ┌──────────────────────────────────────┐
│  VINCULAÇÃO DE CONTACTOS (NÓS)       │                  │  ARESTAS DE INTERAÇÃO                │
│  Mapeia automaticamente:             │                  │  Linhas que unem as pessoas com:     │
│  • Nuno Duarte                       │                  │  • Número total de mensagens         │
│  • Dr. Varela de Matos               │                  │  • Chamadas e anexos trocados        │
│  • AE Luísa Santos                   │                  │  • Linha temporal de frequência      │
│  • Filipe Delgado / Teresa Martins   │                  │  • Deteção de conluio e grupos       │
└──────────────────────────────────────┘                  └──────────────────────────────────────┘
```

### Como Ativar o Gráfico no Autopsy:
1. No menu superior do Autopsy, clique em **"Tools" ➔ "Communications"** (ou no ícone de mensagens na barra de ferramentas).
2. Na aba lateral, selecione **"Accounts"** (Contas) ou **"Contacts"** (Contactos).
3. Selecione os intervenientes (ex: *Filipe Delgado, Teresa, Nuno, Dr. Varela*).
4. Clique no separador **"Browse Graph" / "Relationship Graph"**:
   - O Autopsy desenha o grafo 2D de vínculos com círculos proporcionais ao número de mensagens trocadas!

---

## 2. O Autopsy e os Plugins em Python (Python Ingest Modules)

O Autopsy foi desenhado com uma API aberta em **Python (Jython)**, permitindo adicionar módulos forenses customizados:

### Principais Plugins Python Suportados pelo Autopsy:
1. **WhatsApp & SQLite Parser**:
   - Analisa diretamente bases de dados `msgstore.db` e tabelas SQLite, reconstruindo todas as conversas e ficheiros áudio `.opus`.
2. **Geolocation / EXIF Map Viewer**:
   - Extrai coordenadas GPS e modelos de câmaras (fotos de câmara Samsung e vídeos de vistoria técnica de 24/05/2024), plotando tudo num mapa geográfico.
3. **Email & EML/MSG Ingest Module**:
   - Descompacta e indexa e-mails de Outlook, Thunderbird e ficheiros `.eml`.
4. **Keyword Search & RegEx Engine**:
   - Varre o disco por expressões regulares (ex: NIFs `254048382`, referências de processos `23142/22`, `3719/25`, `10153/24`).
5. **Timeline Analyzer (Linha Temporal)**:
   - Ordena minuto a minuto todas as ações que ocorreram nos discos de 2018, 2019 e 2022.

---

## 3. O Plugin Python Criado para o Seu Caso

Criámos o módulo Python específico para injetar todo o acervo de dados do Dev Yokozuna no Autopsy:
- 👉 [`autopsy_yokozuna_ingest_plugin.py`](file:///C:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/scripts/autopsy_yokozuna_ingest_plugin.py)

### Como Instalar o Plugin no Autopsy:
1. No Autopsy, vá ao menu: **Tools ➔ Python Plugins**.
2. Clique no botão **"Open Python Plugin Folder"** (Abre a pasta `%APPDATA%\autopsy\python_modules`).
3. Copie o ficheiro `autopsy_yokozuna_ingest_plugin.py` para dentro dessa pasta.
4. Reinicie o Autopsy — o módulo aparecerá na lista de opções de ingestão!
