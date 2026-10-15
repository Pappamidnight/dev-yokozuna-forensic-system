@echo off
chcp 65001 >nul
cd /d C:\ACERVO\scripts\acervo
python -u pipeline.py
pause
