# Guia Forense: Recuperação de Dados e Desbloqueio de Telemóveis OPPO e HUAWEI (Ecrã Partido)

**Data**: 2026-08-28  
**Autoridade**: Sistema Forense Dev Yokozuna  
**Dispositivos**: OPPO (ColorOS) e HUAWEI (EMUI / HarmonyOS) com ecrã danificado  
**Objetivo**: Recuperar WhatsApp, mensagens, fotos e bases de dados

---

## 1. Método Universal 100% Eficaz: Teclado USB + Adaptador OTG

Tanto os telemóveis **OPPO** como os **HUAWEI** reconhecem teclados de computador imediatamente pela porta USB Type-C:

```
┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
│ TECLADO USB DO          │ ────> │ ADAPTADOR USB-C (OTG)   │ ────> │ TELEMÓVEL OPPO / HUAWEI │
│ COMPUTADOR              │       │ (Adaptador de 2€ a 5€)  │       │ COM ECRÃ PARTIDO        │
└─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
```

### Passos:
1. Ligue o teclado do computador à porta USB-C do Oppo ou Huawei com o adaptador OTG.
2. Prima a **Barra de Espaço** ou **Enter** 2 vezes (o ecrã acende no escuro e foca o campo do código PIN).
3. Escreva o seu **PIN numérico ou Password** no teclado.
4. Prima a tecla **Enter**.
5. O telemóvel desbloqueia instantaneamente!
6. Desligue o teclado e ligue o cabo USB ao PC. O computador terá acesso imediato aos ficheiros e à memória interna.

---

## 2. Recuperação do Telemóvel HUAWEI

### Opção A: Huawei Cloud no Navegador do PC
Se tinha a conta Huawei ativa no telemóvel:
1. Abra no navegador do PC: **[cloud.huawei.com](https://cloud.huawei.com)**
2. Inicie sessão com a sua conta Huawei / e-mail.
3. Aceda diretamente a:
   - **Galeria de Fotografias e Vídeos**
   - **Contactos e Histórico de Chamadas**
   - **Bloco de Notas e Ficheiros da Huawei Drive**
   - **Cópias de Segurança de Aplicações**

### Opção B: Huawei HiSuite (Software Oficial no PC)
1. Instale o **Huawei HiSuite** no computador.
2. Ligue o cabo USB. O programa permite fazer um backup integral para o computador.

---

## 3. Recuperação do Telemóvel OPPO

### Opção A: OPPO Cloud / HeyTap no Navegador do PC
1. Abra no navegador do PC: **[cloud.heytap.com](https://cloud.heytap.com)**
2. Inicie sessão com o seu número de telefone ou e-mail registado no Oppo.
3. Permite descarregar fotografias, contactos e cópias de segurança.

### Opção B: Desbloqueio e Extração via Cabo USB (ADB)
Com o telemóvel ligado por USB ao PC:
1. Execute na pasta do projeto:
   [ITEM]  [`DESBLOQUEAR_TELEMOVEL_ADB.bat`](file:///C:/Users/Yokozuna/Dev/DESBLOQUEAR_TELEMOVEL_ADB.bat) (digite o PIN no teclado do PC).
2. Execute a seguir:
   [ITEM]  [`EXTRAIR_DADOS_TELEMOVEL_ADB.bat`](file:///C:/Users/Yokozuna/Dev/EXTRAIR_DADOS_TELEMOVEL_ADB.bat) (extrai todo o WhatsApp e DCIM).

---

## 4. Recuperação das Conversas do WhatsApp via Google Drive

Como o WhatsApp nos dispositivos Android (Oppo e Huawei com serviços Google) faz cópia de segurança diária para a sua conta Google (`nunomiguelsilvaduarte@gmail.com`):

1. Todas as conversas de WhatsApp continuam guardadas no **Google Drive Backups**.
2. Pode verificar o estado das cópias em: **[Google Drive - Cópias de Segurança](https://drive.google.com/drive/backups)**.
3. Ao instalar o WhatsApp em qualquer outro telemóvel ou emulador no PC com o seu cartão SIM/número, todas as mensagens, áudios e fotografias são restauradas automaticamente.
