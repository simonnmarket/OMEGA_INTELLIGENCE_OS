@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V1.2 - INICIANDO SISTEMA (MONITORAMENTO)
echo ============================================================
echo.
echo Sistema: Prometheus v1.2 (Monitoramento)
echo Modo: TODOS OS ATIVOS DO MARKET WATCH
echo Estratégia: MA20 ^> MA50 = BUY
echo Monitoramento: Fecha posições quando sinal BUY é perdido
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v1.2_monitoramento.py
pause

