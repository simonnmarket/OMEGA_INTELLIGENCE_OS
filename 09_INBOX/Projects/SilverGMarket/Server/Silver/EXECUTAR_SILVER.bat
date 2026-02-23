@echo off
chcp 65001 >nul
cls
echo ============================================================
echo SILVER SYSTEM V2.3 - PROJETO SILVERGMARKET
echo ============================================================
echo.
echo Sistema: Silver System v2.3
echo Projeto: SilverGMarket (Independente)
echo Símbolos: XAGUSD, XAGAUD, XAGEUR, XAGGBP
echo Magic Number: 99992 (isolado)
echo.
echo ============================================================
echo.
cd /d "%~dp0"

echo Verificando horário de trading...
python verificar_horario_trading_xag.py
echo.
echo ============================================================
echo Iniciando Sistema Silver...
echo ============================================================
echo.

python silver_system_v2.3.py

pause

