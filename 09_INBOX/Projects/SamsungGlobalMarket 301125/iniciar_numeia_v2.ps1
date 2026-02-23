# Script de Inicialização - Numeia v2.0 (PowerShell)
# Executa o sistema a partir do diretório correto

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\Server\Numeia"
python numeia_executor_v2.py

