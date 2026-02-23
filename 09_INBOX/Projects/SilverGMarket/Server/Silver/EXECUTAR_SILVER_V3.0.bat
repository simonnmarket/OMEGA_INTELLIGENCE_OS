@echo off
chcp 65001 >nul
cls
echo ============================================================
echo SILVER SYSTEM V3.0 - ESCALONADO COM MULTIPLAS ENTRADAS
echo Projeto: SilverGMarket (Independente)
echo ============================================================
echo.
echo Sistema: Silver System v3.0 ESCALONADO
echo Timeframe: M1 (múltiplas entradas)
echo Volume: 0.10 - 50.00 lotes (escalonado)
echo Entradas: Ilimitadas por símbolo
echo SL/TP: 100/800 pips (tendências grandes)
echo.
echo ============================================================
echo.
cd /d "%~dp0"

echo Verificando horário de trading...
python verificar_horario_trading_xag.py
echo.
echo ============================================================
echo Iniciando Sistema Silver V3.0 ESCALONADO...
echo Sistema rodará durante a noite inteira
echo ============================================================
echo.

python silver_system_v3.0_escalonado.py

pause

