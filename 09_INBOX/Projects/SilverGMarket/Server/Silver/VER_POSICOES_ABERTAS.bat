@echo off
chcp 65001 >nul
cls
echo ============================================================
echo SILVER SYSTEM V3.0 - VER POSICOES ABERTAS
echo ============================================================
echo.
cd /d "%~dp0"

python VER_POSICOES_ABERTAS.py

echo.
pause

