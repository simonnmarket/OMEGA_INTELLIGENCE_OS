@echo off
chcp 65001 >nul
cls
echo ============================================================
echo PROMETHEUS V2.3 - MODO TESTE (XAG)
echo ============================================================
echo.
echo Sistema: Prometheus v2.3 (Modo Teste)
echo Símbolos: XAGUSD, XAGAUD, XAGEUR, XAGGBP
echo.
echo Verificando configuração...
echo.
cd /d "%~dp0"

python -c "from prometheus_config_test import TEST_MODE, TEST_SYMBOLS; print(f'TEST_MODE: {TEST_MODE}'); print(f'Símbolos: {TEST_SYMBOLS}')" 2>nul
if errorlevel 1 (
    echo ⚠️ Erro ao carregar configuração. Verifique prometheus_config_test.py
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Iniciando sistema em modo teste...
echo ============================================================
echo.
python prometheus_v2.3_gerenciamento_escalonado.py

pause

