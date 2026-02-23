@echo off
chcp 65001 >nul
cls
echo ============================================================
echo SILVER SYSTEM V3.0 - VERIFICAR RESULTADOS DA NOITE
echo ============================================================
echo.
cd /d "%~dp0"

echo Analisando logs e resultados...
echo.
python ANALISAR_RESULTADOS_AMANHA.py

echo.
echo ============================================================
echo Pressione qualquer tecla para sair...
pause >nul

