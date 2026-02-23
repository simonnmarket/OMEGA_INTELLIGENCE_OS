@echo off
chcp 65001 >nul
cls
echo ============================================================
echo ANALISE DE ENTRADAS PREMATURAS - VALIDACAO DA ESTRATEGIA
echo ============================================================
echo.
cd /d "%~dp0"

python ANALISE_ENTRADAS_PREMATURAS.py

echo.
pause

