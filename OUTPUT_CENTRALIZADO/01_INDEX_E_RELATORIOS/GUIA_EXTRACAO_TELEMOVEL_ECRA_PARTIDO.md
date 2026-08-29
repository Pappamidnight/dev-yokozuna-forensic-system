# Guia Forense: Extração de Dados de Telemóvel com Ecrã Partido e Comandos de Pesquisa Rápida

**Data**: 2026-08-28  
**Autoridade**: Sistema Forense Dev Yokozuna  
**Cenário**: Dispositivo Android com ecrã danificado/partido ligado por cabo USB ao computador.

---

## 1. Como Ver e Controlar o Telemóvel no Ecrã do PC (scrcpy)

Se o telemóvel tiver a Depuração USB (*USB Debugging*) ativa:
1. **Espelhar o Ecrã no Computador**:
   ```bash
   scrcpy
   ```
   *Permite ver todo o ecrã no monitor do PC e clicar com o rato como se fosse o dedo no vidro partido.*
2. **Desbloquear o Ecrã se o Teclado/Touch não funcionar**:
   ```bash
   scrcpy --turn-screen-off
   ```
   *(Ou digitar o código PIN diretamente pelo teclado do PC).*

---

## 2. Comandos ADB para Extrair Todas as Mensagens e Fotos do Telemóvel

Com o telemóvel ligado por USB, execute estes comandos no terminal:

### Passo A: Verificar se o telemóvel está reconhecido
```powershell
adb devices
```
*(Deverá listar o código do telemóvel seguido de `device`).*

### Passo B: Extrair todo o WhatsApp (Bases de Dados, Áudios e Mensagens)
```powershell
# Cria a pasta de destino
mkdir C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp -Force

# Extrai o WhatsApp moderno (Android 11, 12, 13, 14)
adb pull /sdcard/Android/media/com.whatsapp/WhatsApp/ C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp\

# Extrai o WhatsApp clássico (Android 10 ou inferior)
adb pull /sdcard/WhatsApp/ C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp\
```

### Passo C: Extrair Todas as Fotografias e Vídeos da Câmara (DCIM)
```powershell
mkdir C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos -Force
adb pull /sdcard/DCIM/ C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos\
```

### Passo D: Fazer Backup Completo do Dispositivo
```powershell
adb backup -apk -shared -all -f C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\backup_telemovel_completo.ab
```

---

## 3. Comandos de Pesquisa Rápida no Computador (Copiar e Colar)

Para pesquisar qualquer termo em todas as conversas do WhatsApp já indexadas no computador:

### 1. Pesquisar por Palavra-Chave em Todas as Conversas
```powershell
# Pesquisar por "Teresa" ou "renda" ou "82"
Get-ChildItem -Path "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO" -Recurse -Filter "*.txt" | Select-String -Pattern "Teresa" | Select-Object -First 30
```

### 2. Pesquisar Linhas de 2021 e 2022 com Filtro de Valores (€)
```powershell
Get-ChildItem -Path "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO" -Recurse -Filter "*whatsapp*.txt" | Select-String -Pattern "(\d{1,2}/\d{1,2}/2[12]).*€"
```

### 3. Pesquisar por Faturas ou NIF no Acervo
```powershell
Get-ChildItem -Path "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO" -Recurse -Filter "*.md" | Select-String -Pattern "254048382"
```

---

## 4. Script Automático Criado no Seu PC

Pode executar diretamente na raiz do Dev:
- [ITEM]  [`PESQUISAR_CONVERSAS.bat`](file:///C:/Users/Yokozuna/Dev/PESQUISAR_CONVERSAS.bat) (digite o termo a pesquisar e ele varre tudo instantaneamente).
- [ITEM]  [`EXTRAIR_DADOS_TELEMOVEL_ADB.bat`](file:///C:/Users/Yokozuna/Dev/EXTRAIR_DADOS_TELEMOVEL_ADB.bat) (extração automática do telemóvel por USB).
