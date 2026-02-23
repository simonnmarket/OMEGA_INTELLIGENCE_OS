@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.2 - ANÁLISE DE PERFORMANCE
echo ============================================================
echo.
echo Sistema: Prometheus v2.2 (Análise de Performance)
echo Objetivo: Analisar logs do V2.1 e gerar métricas
echo.
echo Métricas Calculadas:
echo   - Win Rate (Taxa de Acerto)
echo   - Profit Factor (Fator de Lucro)
echo   - Break-Even Hit Rate
echo   - Trailing Stop Moves
echo   - Análise por Símbolo
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.2_analise_performance.py
pause

