@echo off
REM ============================================================================
REM AURORA v5.1 - INICIALIZAÇÃO DO PROCESSO CRYPTO
REM ============================================================================
REM Inicia o sistema Aurora com estratégias ativadas para operação em CRYPTO
REM ============================================================================

echo ============================================================================
echo AURORA v5.1 - INICIALIZACAO DO PROCESSO CRYPTO
echo ============================================================================
echo.
echo [INFO] Estrategias ativadas:
echo    - Alpha Momentum Strategy
echo    - Mean Reversion Strategy  
echo    - Breakout Detection Strategy
echo.
echo [INFO] Iniciando FASE ALPHA (teste cientifico - 30 minutos)...
echo.

cd /d "%~dp0"

REM Executar FASE α
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py alpha

if errorlevel 1 (
    echo.
    echo [ERRO] FASE ALPHA falhou. Verifique os logs.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] FASE ALPHA concluida!
echo [INFO] Verifique os relatorios gerados.
echo.
echo [PROXIMO PASSO] Para executar FASE BETA (24h):
echo    python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta
echo.

pause

