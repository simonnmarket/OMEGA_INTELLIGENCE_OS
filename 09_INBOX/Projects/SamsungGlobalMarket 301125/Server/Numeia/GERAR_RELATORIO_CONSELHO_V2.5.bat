@echo off
chcp 65001 >nul
cls
echo ============================================================
echo PROMETHEUS V2.5 - RELATÓRIO EXECUTIVO PARA CONSELHO
echo ============================================================
echo.
echo Sistema: Prometheus v2.5 (Relatório Executivo)
echo Objetivo: Gerar relatório formatado para apresentação ao conselho
echo.
echo Processo:
echo   1. Gerar relatório científico (JSON)
echo   2. Converter para relatório executivo (Markdown)
echo.
echo ============================================================
echo.
cd /d "%~dp0"

echo [1/2] Gerando relatório científico...
python prometheus_v2.5_relatorio_cientifico.py
if errorlevel 1 (
    echo.
    echo ERRO: Falha ao gerar relatório científico!
    echo Verifique se o Python está instalado e se os arquivos existem.
    pause
    exit /b 1
)

echo.
echo [2/2] Gerando relatório executivo para conselho...
python prometheus_v2.5_relatorio_executivo.py
if errorlevel 1 (
    echo.
    echo ERRO: Falha ao gerar relatório executivo!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo RELATÓRIO GERADO COM SUCESSO!
echo ============================================================
echo.
echo Arquivos gerados:
if exist "PROMETHEUS_RELATORIO_CONSELHO_V2.5.md" (
    echo   [OK] PROMETHEUS_RELATORIO_CONSELHO_V2.5.md (Relatório Executivo)
) else (
    echo   [ERRO] PROMETHEUS_RELATORIO_CONSELHO_V2.5.md (NÃO ENCONTRADO)
)
if exist "prometheus_relatorio_cientifico_v2.5.json" (
    echo   [OK] prometheus_relatorio_cientifico_v2.5.json (Dados Técnicos)
) else (
    echo   [ERRO] prometheus_relatorio_cientifico_v2.5.json (NÃO ENCONTRADO)
)
echo.
echo O relatório executivo está pronto para apresentação ao conselho.
echo.
echo Localização: %CD%
echo.
pause

