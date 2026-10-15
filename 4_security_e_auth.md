# Seguranca, Autenticacao e Blindagem: Acervo Forense V8

**Versao**: 8.0.0 Canónica  
**Data**: 2026-10-15  
**Ambiente**: Universal Antigravity / Host Windows 11 / WSL2 Kali  

---

## 1. Modelo de Ameacas e Perimetro de Defesa

O sistema opera sob o pressuposto de ambiente adverso (host potencialmente poluído, discos compartilhados, exposicao acidental de dados privados ou manipulacao indevida de provas). A estrategia de defesa baseia-se em:
1. **Isolamento Estrito de Ambientes**: Segregação fisica e logica entre codigo versionado e dados forenses pesados.
2. **Deflexao de Credenciais**: Banimento total de tokens, chaves de API e palavras-passe em repositorios publicos ou commits de controlo de versao.
3. **Imutabilidade Operacional**: Operacoes de leitura nao produzem escritas colaterais nos diretorios de prova original.

---

## 2. Politica de Gestao de Segredos e Credenciais

- **Ficheiros Ignorados Compulsoriamente**:
  - `.env`, `.env.*`
  - `secrets/`
  - `backups/`
  - `*.key`, `*.pem`, `*.pfx`
- **Injecao de Variaveis em Runtime**:
  - As chaves de acesso a servicos remotos (LLMs, gateways, S3) sao carregadas exclusivamente atraves do ambiente de execucao (`os.environ.get`) ou cofre local encriptado.
  - Proibido o commit de credenciais em ficheiros de teste ou exemplos de configuracao.

---

## 3. Integridade Criptografica e Cadeia de Custodia

- **Algoritmo de Hashing Padrao**: SHA-256 (NIST FIPS 180-4).
- **Verificacao Multi-Sinal**: Validacao cruzada de hash, tamanho exato em bytes e timestamps NTFS (`MTime`, `CTime`).
- **Detecao de Corrupcao**: Qualquer discrepancia entre o hash indexado e o ficheiro no disco gera um alarme de violacao de custodia e bloqueia a utilizacao do artefacto em pecas processuais.

---

## 4. Controlo de Execucao em Terminal e Subprocessos

1. **Sandboxing Controlado**:
   - Comandos com necessidade de acesso a rede ou sistemas externos sao declarados explicitamente com aprovacao manual (`BypassSandbox: true`).
   - Comandos de leitura local e analise documental operam estritamente isolados (`BypassSandbox: false`).
2. **Resiliencia de Sistema Operativo (Windows P-03)**:
   - Todo o acesso ao disco esta protegido contra ficheiros bloqueados ou fantasmas (`try...except OSError`).
   - Em caso de bloqueio por outro processo do SO, o motor deflete silenciosamente sem quebrar a execucao global.
3. **Restricao de Executaveis Legados**:
   - Banimento estrito de `es.exe` devido a vulnerabilidades de truncagem e encoding; utilizacao mandataria da API REST HTTP do Everything na porta 8080.
