@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.4 - ANÁLISE AVANÇADA DE PERFORMANCE
echo ============================================================
echo.
echo Sistema: Prometheus v2.4 (Análise Avançada)
echo Objetivo: Analisar logs do V2.3 e gerar métricas avançadas
echo.
echo Métricas Calculadas:
echo   - Win Rate (Taxa de Acerto)
echo   - Profit Factor (Fator de Lucro)
echo   - Expectancy (Expectativa)
echo   - Maximum Drawdown (MDD)
echo   - Sharpe Ratio (Risco/Retorno)
echo   - Win/Loss Ratio
echo   - Análise de TP Parcial (V2.3)
echo   - Análise por Símbolo
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.4_analise_avancada.py
pause

