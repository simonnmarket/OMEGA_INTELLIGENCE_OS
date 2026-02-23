@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V1.0 MVPO - INICIANDO SISTEMA
echo ============================================================
echo.
echo Sistema: Prometheus v1.0 (Mínimo Viável Operacional)
echo Modo: TODOS OS ATIVOS DO MARKET WATCH
echo Estratégia: MA5 ^> MA20 = BUY
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v1.0_mvpo.py
pause

