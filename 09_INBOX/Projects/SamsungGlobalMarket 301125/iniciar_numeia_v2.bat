@echo off
REM Script de Inicialização - Numeia v2.0
REM Executa o sistema a partir do diretório correto

cd /d "%~dp0Server\Numeia"
python numeia_executor_v2.py
pause

