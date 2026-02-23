# SCRIPT PARA CORRIGIR CAMINHO DO .ex5
# Projeto Prometheus v3.0.0 | Samsung Global Market

Write-Host "===========================================================================" -ForegroundColor Red
Write-Host "CORRECAO CRITICA: ARQUIVO .ex5 EM CAMINHO ERRADO" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

$mt5Path = "$env:APPDATA\MetaQuotes\Terminal"

Write-Host "[1/3] Buscando arquivos .ex5..." -ForegroundColor Cyan

# Buscar TODOS os arquivos .ex5 do EA
$ex5Files = Get-ChildItem -Path $mt5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($ex5Files.Count -eq 0) {
    Write-Host "  [AVISO] Nenhum arquivo .ex5 encontrado" -ForegroundColor Yellow
    Write-Host "  Isso pode estar ok se EA ainda nao foi compilado" -ForegroundColor Gray
} else {
    Write-Host "  [INFO] Encontrados $($ex5Files.Count) arquivo(s) .ex5:" -ForegroundColor Yellow
    Write-Host ""
    
    $caminhoErrado = $null
    $caminhoCorreto = $null
    
    foreach ($file in $ex5Files) {
        $fullPath = $file.FullName
        $mtime = $file.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')
        
        Write-Host "  Arquivo: $fullPath" -ForegroundColor White
        Write-Host "    Modificado: $mtime" -ForegroundColor Gray
        
        # Verificar se está no caminho errado (tem subpasta SamsungGlobalMarket/Experts/)
        if ($fullPath -like "*\SamsungGlobalMarket\Experts\SamsungGlobalMarket_EA.ex5") {
            Write-Host "    STATUS: [ERRO] CAMINHO ERRADO (subpasta duplicada)" -ForegroundColor Red
            $caminhoErrado = $file
        }
        # Verificar se está no caminho correto (direto em Experts/)
        elseif ($fullPath -like "*\Experts\SamsungGlobalMarket_EA.ex5" -and $fullPath -notlike "*\SamsungGlobalMarket\*") {
            Write-Host "    STATUS: [OK] CAMINHO CORRETO" -ForegroundColor Green
            $caminhoCorreto = $file
        }
        else {
            Write-Host "    STATUS: [AVISO] Caminho suspeito" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    Write-Host "[2/3] Deletando arquivo(s) do caminho errado..." -ForegroundColor Cyan
    
    if ($caminhoErrado) {
        Write-Host "  Deletando: $($caminhoErrado.FullName)" -ForegroundColor Yellow
        try {
            Remove-Item $caminhoErrado.FullName -Force
            Write-Host "  [OK] Arquivo deletado com sucesso" -ForegroundColor Green
        } catch {
            Write-Host "  [ERRO] Falha ao deletar: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [INFO] Nenhum arquivo em caminho errado encontrado" -ForegroundColor Gray
    }
    
    # Também deletar se caminho correto existe mas é antigo (forçar recompilação)
    if ($caminhoCorreto) {
        $idade = (Get-Date) - $caminhoCorreto.LastWriteTime
        if ($idade.TotalMinutes -gt 30) {
            Write-Host ""
            Write-Host "  [AVISO] Arquivo no caminho correto mas antigo ($([math]::Round($idade.TotalMinutes, 1)) minutos)" -ForegroundColor Yellow
            Write-Host "  Deletando para forcar recompilacao..." -ForegroundColor Yellow
            try {
                Remove-Item $caminhoCorreto.FullName -Force
                Write-Host "  [OK] Arquivo antigo deletado" -ForegroundColor Green
            } catch {
                Write-Host "  [ERRO] Falha ao deletar: $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "[3/3] Instrucoes finais:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  CAMINHO CORRETO PARA O .mq5:" -ForegroundColor Yellow
Write-Host "    $mt5Path\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5" -ForegroundColor White
Write-Host ""
Write-Host "  PROXIMOS PASSOS:" -ForegroundColor Green
Write-Host "    1. Abrir MetaEditor" -ForegroundColor Cyan
Write-Host "    2. Abrir arquivo do caminho correto acima" -ForegroundColor Cyan
Write-Host "    3. Verificar linha 8: #property version `"1.05`"" -ForegroundColor Cyan
Write-Host "    4. Compilar (F7)" -ForegroundColor Cyan
Write-Host "    5. Validar que .ex5 foi gerado em:" -ForegroundColor Cyan
Write-Host "       ...\Experts\SamsungGlobalMarket_EA.ex5 (SEM subpastas)" -ForegroundColor White
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green

