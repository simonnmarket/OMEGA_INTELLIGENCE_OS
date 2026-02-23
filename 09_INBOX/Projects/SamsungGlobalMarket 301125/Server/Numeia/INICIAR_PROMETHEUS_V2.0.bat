@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.0 - INICIANDO SISTEMA (TELEMETRIA)
echo ============================================================
echo.
echo Sistema: Prometheus v2.0 (Telemetria)
echo Modo: TODOS OS ATIVOS DO MARKET WATCH
echo Estratégia: MA20 ^> MA50 = BUY
echo Monitoramento: Fecha posições quando sinal BUY é perdido
echo Telemetria: Logging JSON estruturado
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.0_telemetria.py
pause

