@echo off
chcp 65001 >nul
cls
echo ==============================================================================
echo   ACERVO FORENSE V8 — PAINEL DE DISPARO SEQUENCIAL (1 TIPO DE CADA VEZ)
echo ==============================================================================
echo.
echo [1] Executar Fase PDF      (P0 - Documentos Judiciais e Certidoes)
echo [2] Executar Fase Imagens  (P1 - Comprovativos, WhatsApp, Faturas)
echo [3] Executar Fase Audios   (P1 - Mensagens de Voz)
echo [4] Executar Fase Videos   (P2 - Videos de Obras e Diligencias)
echo [5] Executar Fase Excel    (P1 - Tabelas de Saldo e Despesas)
echo [6] Executar Fase Word     (P2 - Minutas e Articulados)
echo [7] Executar Todas as Fases Sequencialmente (Modo Auditoria)
echo [8] Ver Relatorios e Manifestos Gerados
echo [9] Executar Motor Rust ML (BLAKE3, Entropia e Features)
echo [0] Sair
echo.
set /p opt="Escolha a opcao [0-9]: "

if "%opt%"=="1" (
    python C:\ACERVO\main.py dedupe --tipo pdf
    pause
    goto fim
)
if "%opt%"=="2" (
    python C:\ACERVO\main.py dedupe --tipo imagem
    pause
    goto fim
)
if "%opt%"=="3" (
    python C:\ACERVO\main.py dedupe --tipo audio
    pause
    goto fim
)
if "%opt%"=="4" (
    python C:\ACERVO\main.py dedupe --tipo video
    pause
    goto fim
)
if "%opt%"=="5" (
    python C:\ACERVO\main.py dedupe --tipo excel
    pause
    goto fim
)
if "%opt%"=="6" (
    python C:\ACERVO\main.py dedupe --tipo word
    pause
    goto fim
)
if "%opt%"=="7" (
    for %%t in (pdf imagem audio video excel word) do (
        echo.
        echo ==============================================================================
        echo A PROCESSAR TIPO: %%t
        echo ==============================================================================
        python C:\ACERVO\main.py dedupe --tipo %%t
    )
    pause
    goto fim
)
if "%opt%"=="8" (
    explorer C:\ACERVO\reports
    goto fim
)
if "%opt%"=="9" (
    echo A compilar e executar o motor Rust de Machine Learning...
    cargo run --manifest-path C:\ACERVO\Cargo.toml -p acervo-forensic-ml --bin forensic-ml
    pause
    goto fim
)
:fim
exit /b 0
