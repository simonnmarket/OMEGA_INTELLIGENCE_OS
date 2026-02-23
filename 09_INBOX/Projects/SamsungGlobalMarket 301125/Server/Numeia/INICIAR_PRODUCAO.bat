@echo off
echo ================================================================================
echo INICIANDO PROMETHEUS V6.0 - PRODUCAO
echo ================================================================================
echo.
echo Sistema: Prometheus v6.0
echo Modo: PRODUCTION
echo Bloqueio SELL: ATIVO
echo ML Adaptativo: ATIVO
echo.
echo ================================================================================
echo.
cd /d "%~dp0"
python run_production_v6.0.py
pause

