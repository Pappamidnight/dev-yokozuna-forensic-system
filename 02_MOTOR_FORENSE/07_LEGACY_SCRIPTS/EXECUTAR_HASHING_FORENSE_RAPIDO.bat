@echo off
chcp 65001 > nul
title MOTOR FORENSE ULTRA-RAPIDO DE HASHING (SHA-256 / MD5 / HASHDEEP)
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO DEV YOKOZUNA - MOTOR FORENSE DE HASHING
echo   Inspirado no padrao Kali Linux Forensics (hashdeep, sha256sum, md5sum)
echo ===============================================================================
echo.
echo [1/3] A verificar ambiente Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    pause
    exit /b 1
)

echo [2/3] A iniciar processamento paralelo multi-core...
python "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\fast_parallel_hasher.py"

echo.
echo [3/3] Processo de hashing concluido com sucesso!
echo Os resultados foram guardados em:
echo   - CSV: OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\MANIFESTO_GLOBAL_HASHES_RAPIDO.csv
echo   - DB : OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\memoria_forense_unificada.db
echo.
echo ===============================================================================
pause
