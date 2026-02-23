# ========================================
# AURORA PROJECT - EXECUTOR DO SISTEMA
# Execucao independente do Cursor
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  AURORA PROJECT - EXECUTOR DO SISTEMA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Navegar para o diretorio do script
Set-Location $PSScriptRoot

Write-Host "Escolha uma opcao:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Executar Sistema Principal (main.py)" -ForegroundColor Cyan
Write-Host "2. Executar Sistema NCNT (main_ncnt.py)" -ForegroundColor Cyan
Write-Host "3. Executar Auditoria Completa" -ForegroundColor Cyan
Write-Host "4. Testar Modulo v2.0" -ForegroundColor Cyan
Write-Host "5. Verificar Instalacao" -ForegroundColor Cyan
Write-Host "6. Executar Relatorio Completo" -ForegroundColor Cyan
Write-Host "7. Sair" -ForegroundColor Cyan
Write-Host ""

$opcao = Read-Host "Digite o numero da opcao"

switch ($opcao) {
    "1" {
        Write-Host ""
        Write-Host "Executando Sistema Principal..." -ForegroundColor Yellow
        Write-Host ""
        python main.py
    }
    "2" {
        Write-Host ""
        Write-Host "Executando Sistema NCNT..." -ForegroundColor Yellow
        Write-Host ""
        python main_ncnt.py
    }
    "3" {
        Write-Host ""
        Write-Host "Executando Auditoria Completa..." -ForegroundColor Yellow
        Write-Host ""
        python 00-Governanca\run_complete_audit.py
    }
    "4" {
        Write-Host ""
        Write-Host "Testando Modulo v2.0..." -ForegroundColor Yellow
        Write-Host ""
        python 00-Governanca\test_module_v2.py
    }
    "5" {
        Write-Host ""
        Write-Host "Verificando Instalacao..." -ForegroundColor Yellow
        Write-Host ""
        if (Test-Path "scripts\verify_installation_v2.ps1") {
            & "scripts\verify_installation_v2.ps1"
        } else {
            Write-Host "Script de verificacao nao encontrado" -ForegroundColor Red
        }
    }
    "6" {
        Write-Host ""
        Write-Host "Executando Relatorio Completo..." -ForegroundColor Yellow
        Write-Host ""
        python 00-Governanca\run_complete_audit.py
        Write-Host ""
        Write-Host "Relatorio gerado em: 05-Documentacao\Audit-Reports\" -ForegroundColor Green
    }
    "7" {
        exit
    }
    default {
        Write-Host "Opcao invalida!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

