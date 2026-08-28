@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXE=python
where python >nul 2>nul
if errorlevel 1 (
  set PYTHON_EXE=C:\Users\Yokozuna\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
)

echo [INGESTAO 15547] A iniciar fabrica multi-agente por 15 minutos...
"%PYTHON_EXE%" "backend\watchdog_runner.py" --root "%~dp0" --seconds 900 --interval 30
echo [INGESTAO 15547] Janela de 15 minutos concluida. Sistema desligado.
endlocal
