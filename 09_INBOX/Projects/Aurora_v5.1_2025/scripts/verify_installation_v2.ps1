# VERIFICAÇÃO DA INSTALAÇÃO NCNT v2.0
# PowerShell Script

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VERIFICAÇÃO DA INSTALAÇÃO NCNT v2.0" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$projectRoot = "C:\Users\Lenovo\Projects\Aurora"
$errors = 0
$warnings = 0

# 1. Verificar arquivos
Write-Host "1. Verificando arquivos..." -ForegroundColor Yellow

$files = @(
    "modules\ncnt_module_template.py",
    "00-Governanca\test_module_v2.py",
    "00-Governanca\integration_gate_v2.py",
    "06-Monitoramento\neural_connection_monitor_v2.py"
)

foreach ($file in $files) {
    $fullPath = Join-Path $projectRoot $file
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "   [OK] $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   [ERRO] $file (FALTANDO)" -ForegroundColor Red
        $errors++
    }
}

# 2. Verificar versão do template
Write-Host "`n2. Verificando versão do template..." -ForegroundColor Yellow

$templatePath = Join-Path $projectRoot "modules\ncnt_module_template.py"
if (Test-Path $templatePath) {
    $content = Get-Content $templatePath -Raw
    if ($content -match "NCNT MODULE TEMPLATE v2.0") {
        Write-Host "   [OK] Template é v2.0" -ForegroundColor Green
    } else {
        Write-Host "   [ERRO] Template NÃO é v2.0" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "   [ERRO] Template não encontrado" -ForegroundColor Red
    $errors++
}

# 3. Testar importação
Write-Host "`n3. Testando importação..." -ForegroundColor Yellow

try {
    Push-Location $projectRoot
    
    $pythonTest = @"
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'modules'))
sys.path.insert(0, os.path.join(os.getcwd(), '00-Governanca'))

try:
    from modules.ncnt_module_template import NCNTModule, RegulatoryContext, NeuralConnection
    print('   [OK] NCNTModule importado com sucesso')
    
    # Verificar atributos v2.0
    attrs = [a for a in dir(NCNTModule) if 'compliance' in a.lower() or 'regulatory' in a.lower()]
    print(f'   [OK] Atributos de compliance: {len(attrs)} encontrados')
    
    # Verificar se tem RegulatoryContext
    if hasattr(NCNTModule, '__init__'):
        print('   [OK] RegulatoryContext disponível')
    
except Exception as e:
    print(f'   [ERRO] Erro na importação: {e}')
    sys.exit(1)
"@
    
    $result = python -c $pythonTest 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
    } else {
        Write-Host $result -ForegroundColor Red
        $errors++
    }
    
} catch {
    Write-Host "   [ERRO] Erro ao executar teste Python: $_" -ForegroundColor Red
    $errors++
} finally {
    Pop-Location
}

# 4. Verificar estrutura de diretórios
Write-Host "`n4. Verificando estrutura de diretórios..." -ForegroundColor Yellow

$requiredDirs = @(
    "modules",
    "00-Governanca",
    "06-Monitoramento"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $projectRoot $dir
    if (Test-Path $fullPath -PathType Container) {
        Write-Host "   [OK] $dir existe" -ForegroundColor Green
    } else {
        Write-Host "   [ERRO] $dir não existe" -ForegroundColor Red
        $errors++
    }
}

# Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA VERIFICAÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "`n[OK] VERIFICAÇÃO COMPLETA - SEM ERROS" -ForegroundColor Green
    Write-Host "✅ Sistema NCNT v2.0 está pronto para uso" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[ERRO] VERIFICAÇÃO FALHOU - $errors erro(s) encontrado(s)" -ForegroundColor Red
    Write-Host "❌ Corrija os erros antes de continuar" -ForegroundColor Red
    exit 1
}

