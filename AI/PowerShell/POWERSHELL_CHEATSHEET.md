# 🚀 COMANDOS POWERSHELL - GUIA E PERFIL CENTRALIZADO

Este guia reúne todas as funções, atalhos e comandos otimizados ativos no seu perfil em [`C:\Users\Yokozuna\Dev\AI\PowerShell\Microsoft.PowerShell_profile.ps1`](file:///C:/Users/Yokozuna/Dev/AI/PowerShell/Microsoft.PowerShell_profile.ps1).

---

## 📍 1. ATALHOS DE NAVEGAÇÃO RÁPIDA (INTEGRADOS NO PERFIL)

```powershell
dev        # Vai direto para C:\Users\Yokozuna\Dev
projects   # Vai direto para C:\Users\Yokozuna\Dev\Projects
backend    # Vai direto para C:\Users\Yokozuna\Dev\Backend
labs       # Vai direto para C:\Users\Yokozuna\Dev\Labs
ai         # Vai direto para C:\Users\Yokozuna\Dev\AI

go dev     # Vai para Dev
go proj    # Vai para Projects
go back    # Vai para Backend
go ai      # Vai para AI
go labs    # Vai para Labs
go docs    # Vai para Documentos
go down    # Vai para Downloads
go desk    # Vai para Desktop
```

---

## 🛠️ 2. FUNÇÕES DE PRODUTIVIDADE ATIVAS NO PERFIL

```powershell
size [Path]                 # Calcula o tamanho total de uma pasta em MB/GB
findbig -Path C:\ -Size 500MB # Encontra ficheiros maiores que 500MB
recent -Days 3              # Lista ficheiros alterados nos últimos 3 dias
cleantemp                   # Limpa automaticamente a pasta Temp do sistema
pathinfo                    # Exibe contagem de ficheiros, pastas e tamanho do diretório atual
mkpath "C:\Caminho\Pasta"   # Cria uma estrutura de diretórios se não existir
whereis python              # Localiza o caminho de um comando instalado
countext                    # Conta e agrupa ficheiros por extensão
touch "ficheiro.txt"        # Cria ou atualiza o timestamp de um ficheiro
```

---

## 🌳 3. FUNÇÕES DE ÁRVORE (TREE)

```powershell
npp-tree-dir                             # Gera tree_dirs.md (apenas pastas)
npp-tree-file                            # Gera tree_full.md (pastas e ficheiros)
npp-tree-depth 3                         # Gera tree_depth.md com profundidade 3
npp-tree-ignore "node_modules,.git"      # Gera tree ignorando padrões
npp-tree-custom -ShowFiles -FileName meumapa.md
```

---

## 📋 4. RECARREGAR PERFIL

Para aplicar instantaneamente qualquer alteração feita no perfil:
```powershell
. $PROFILE
```
