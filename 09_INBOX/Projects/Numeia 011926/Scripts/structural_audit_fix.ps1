# AUDITORIA ESTRUTURAL E CORREÇÃO - PROTOCOLO TIER-0
Write-Host "=== AUDITORIA ESTRUTURAL E CORREÇÃO ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Protocolo: GOVERNANCE MANIFEST COMPLIANCE" -ForegroundColor Cyan
Write-Host ""

# FASE 1: VERIFICAR ESTRUTURA OFICIAL
Write-Host "FASE 1: Verificando estrutura oficial..." -ForegroundColor Magenta

$officialStructure = @{
    "core" = "Núcleo central de controle da EA"
    "agents" = "Agentes inteligentes operacionais"
    "utils" = "Ferramentas auxiliares e scripts"
    "config" = "Configurações iniciais e chaves globais"
    "risk" = "Módulo institucional de risco e proteção"
    "include" = "Diretório principal de includes"
    "auditor" = "Módulos de auditoria, verificação e autocorreção"
    "expert" = "Arquivo principal .mq5 da EA"
    "scripts" = "Scripts auxiliares, testes e execução offline"
    "logs" = "Logs operacionais e institucionais"
    "docs" = "Documentação técnica, guias e manifestos"
}

$missingDirs = @()
$emptyDirs = @()

foreach ($dir in $officialStructure.Keys) {
    if (!(Test-Path $dir)) {
        $missingDirs += $dir
        Write-Host "❌ AUSENTE: $dir - $($officialStructure[$dir])" -ForegroundColor Red
    } else {
        $fileCount = (Get-ChildItem $dir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        if ($fileCount -eq 0) {
            $emptyDirs += $dir
            Write-Host "⚠️ VAZIO: $dir - $($officialStructure[$dir])" -ForegroundColor Yellow
        } else {
            Write-Host "✅ OK: $dir ($fileCount arquivos) - $($officialStructure[$dir])" -ForegroundColor Green
        }
    }
}

# FASE 2: VERIFICAR INCLUDES INCORRETOS
Write-Host ""
Write-Host "FASE 2: Verificando includes incorretos..." -ForegroundColor Magenta

$allFiles = Get-ChildItem -Recurse -Include "*.mqh", "*.mq5"
$incorrectIncludes = @()

foreach ($file in $allFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            # Verificar includes que não seguem a arquitetura
            $includePattern = '#include\s+<([^>]+)>'
            $matches = [regex]::Matches($content, $includePattern)
            
            foreach ($match in $matches) {
                $includePath = $match.Groups[1].Value
                
                # Verificar se o include segue a arquitetura oficial
                $isValid = $false
                foreach ($officialDir in $officialStructure.Keys) {
                    if ($includePath.StartsWith($officialDir + "/")) {
                        $isValid = $true
                        break
                    }
                }
                
                if (!$isValid) {
                    $incorrectIncludes += @{
                        File = $file.Name
                        Include = $includePath
                        Path = $file.FullName
                    }
                }
            }
        }
    } catch {
        Write-Host "Erro ao ler: $($file.Name)" -ForegroundColor Red
    }
}

# FASE 3: RELATÓRIO DE AUDITORIA
Write-Host ""
Write-Host "FASE 3: Gerando relatório de auditoria..." -ForegroundColor Magenta

$complianceStatus = if ($missingDirs.Count -eq 0) { "SIM" } else { "NÃO" }
$structureComplete = if ($missingDirs.Count -eq 0) { "SIM" } else { "NÃO" }
$includesCorrect = if ($incorrectIncludes.Count -eq 0) { "SIM" } else { "NÃO" }

$reportContent = @"
=== AUDITORIA ESTRUTURAL - GOVERNANCE MANIFEST COMPLIANCE ===
Data: $(Get-Date)
Protocolo: TIER-0 STRUCTURAL AUDIT
Status: VERIFICAÇÃO ESTRUTURAL CONCLUÍDA

=== ESTRUTURA OFICIAL vs REAL ===

DIRETÓRIOS AUSENTES ($($missingDirs.Count)):
"@

foreach ($dir in $missingDirs) {
    $reportContent += "`n❌ $dir - $($officialStructure[$dir])"
}

$reportContent += @"

DIRETÓRIOS VAZIOS ($($emptyDirs.Count)):
"@

foreach ($dir in $emptyDirs) {
    $reportContent += "`n⚠️ $dir - $($officialStructure[$dir])"
}

$reportContent += @"

=== INCLUDES INCORRETOS ($($incorrectIncludes.Count)) ===
"@

foreach ($incorrect in $incorrectIncludes) {
    $reportContent += "`n❌ $($incorrect.File) -> $($incorrect.Include)"
}

$reportContent += @"

=== AÇÕES NECESSÁRIAS ===
1. Criar diretórios ausentes: $($missingDirs.Count)
2. Preencher diretórios vazios: $($emptyDirs.Count)
3. Corrigir includes incorretos: $($incorrectIncludes.Count)
4. Atualizar relatórios de arquitetura

=== STATUS FINAL ===
- Conformidade com Governance Manifest: $complianceStatus
- Estrutura completa: $structureComplete
- Includes corretos: $includesCorrect
"@

$reportPath = "structural_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Set-Content $reportPath $reportContent

Write-Host ""
Write-Host "=== AUDITORIA ESTRUTURAL CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Relatório salvo: $reportPath" -ForegroundColor Green
Write-Host "Diretórios ausentes: $($missingDirs.Count)" -ForegroundColor $(if ($missingDirs.Count -eq 0) { 'Green' } else { 'Red' })
Write-Host "Diretórios vazios: $($emptyDirs.Count)" -ForegroundColor $(if ($emptyDirs.Count -eq 0) { 'Green' } else { 'Yellow' })
Write-Host "Includes incorretos: $($incorrectIncludes.Count)" -ForegroundColor $(if ($incorrectIncludes.Count -eq 0) { 'Green' } else { 'Red' })