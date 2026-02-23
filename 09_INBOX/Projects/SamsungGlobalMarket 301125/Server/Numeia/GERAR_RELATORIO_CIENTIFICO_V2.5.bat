@echo off
chcp 65001 >nul
echo ============================================================
echo PROMETHEUS V2.5 - RELATÓRIO CIENTÍFICO DE PERFORMANCE
echo ============================================================
echo.
echo Sistema: Prometheus v2.5 (Relatório Científico)
echo Objetivo: Análise quantitativa completa em formato JSON
echo.
echo Seções do Relatório:
echo   - Relatório de Ordens Executadas
echo   - Métricas de Performance
echo   - Análise de Eficácia da Estratégia (MA5/MA20)
echo   - Contexto de Mercado
echo   - Métricas de Validação de Hipóteses (H1-H4)
echo   - Saúde do Sistema
echo   - Análise CEO Científica
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python prometheus_v2.5_relatorio_cientifico.py
pause

