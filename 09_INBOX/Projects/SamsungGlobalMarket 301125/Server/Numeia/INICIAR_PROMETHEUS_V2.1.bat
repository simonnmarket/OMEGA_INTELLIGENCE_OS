@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.1 - INICIANDO SISTEMA (GESTÃO DE RISCO)
echo ============================================================
echo.
echo Sistema: Prometheus v2.1 (Gestão de Risco Avançada)
echo Modo: TODOS OS ATIVOS DO MARKET WATCH
echo Estratégia: MA20 ^> MA50 = BUY
echo Monitoramento: Fecha posições quando sinal BUY é perdido
echo Break-Even: Move SL para entrada quando lucro ^>= 15 pips
echo Trailing Stop: Move SL seguindo o preço (20 pips)
echo Telemetria: Logging JSON estruturado
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.1_gestao_risco.py
pause

