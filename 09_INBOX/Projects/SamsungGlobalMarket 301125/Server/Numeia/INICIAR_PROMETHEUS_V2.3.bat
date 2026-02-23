@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.3 - INICIANDO SISTEMA (GERENCIAMENTO ESCALONADO)
echo ============================================================
echo.
echo Sistema: Prometheus v2.3 (Gerenciamento Escalonado)
echo Modo: TODOS OS ATIVOS DO MARKET WATCH
echo Estratégia: MA20 ^> MA50 = BUY
echo Volume Inicial: 0.02 lotes
echo TP Parcial: Fecha 50%% (0.01) em 40 pips
echo TP Final: 80 pips (volume restante)
echo Break-Even: Move SL para entrada quando lucro ^>= 15 pips
echo Trailing Stop: Move SL seguindo o preço (20 pips)
echo Telemetria: Logging JSON estruturado
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.3_gerenciamento_escalonado.py
pause

