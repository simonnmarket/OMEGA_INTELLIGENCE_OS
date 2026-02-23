@echo off
chcp 65001 >nul
cls
echo ============================================================
echo PROMETHEUS SILVER V2.3 - SISTEMA ESPECIALIZADO EM PRATA
echo ============================================================
echo.
echo Sistema: Prometheus Silver v2.3
echo Símbolos: XAGUSD, XAGAUD, XAGEUR, XAGGBP
echo Magic Number: 99992 (isolado do sistema principal)
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

python prometheus_silver_v2.3.py

pause

