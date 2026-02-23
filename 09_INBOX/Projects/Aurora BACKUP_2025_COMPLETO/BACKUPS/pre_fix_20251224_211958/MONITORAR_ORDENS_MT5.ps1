#!/usr/bin/env pwsh
# ============================================================================
# AURORA v5.1 - MONITORAMENTO DE ORDENS MT5 EM TEMPO REAL
# ============================================================================
# Script para monitorar ordens sendo enviadas ao MetaTrader 5
# Execute em um terminal separado enquanto o sistema roda
# ============================================================================

$ErrorActionPreference = "Continue"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Clear-Host
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "           AURORA v5.1 - MONITORAMENTO DE ORDENS MT5" "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"
Write-Host ""

# Verificar se MT5 está rodando
Write-ColorOutput "🔍 Verificando MetaTrader 5..." "Cyan"
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-ColorOutput "✅ MetaTrader 5 está rodando (PID: $($mt5Process.Id))" "Green"
} else {
    Write-ColorOutput "⚠️  MetaTrader 5 não está rodando!" "Yellow"
    Write-ColorOutput "   Abra o MetaTrader 5 para ver as ordens" "Yellow"
}

Write-Host ""

# Script Python para monitorar MT5
$monitorScript = @"
import sys
import time
from pathlib import Path
from datetime import datetime

# Adicionar caminho
sys.path.insert(0, str(Path('04-Infraestrutura')))

try:
    from mt5_executor import MT5Executor
    import MetaTrader5 as mt5
    
    print("=" * 60)
    print("🔌 CONECTANDO AO METATRADER 5...")
    print("=" * 60)
    
    executor = MT5Executor()
    
    if not executor.connected:
        print("❌ Não foi possível conectar ao MT5")
        print("   Verifique se o MetaTrader 5 está aberto")
        sys.exit(1)
    
    print("✅ Conectado ao MetaTrader 5")
    print("")
    print("=" * 60)
    print("📊 MONITORAMENTO DE ORDENS EM TEMPO REAL")
    print("=" * 60)
    print("Pressione Ctrl+C para parar")
    print("")
    
    last_order_count = 0
    last_position_count = 0
    
    while True:
        # Obter estatísticas
        stats = executor.get_statistics()
        positions = executor.get_positions()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Verificar novas ordens
        if stats['orders_sent'] > last_order_count:
            new_orders = stats['orders_sent'] - last_order_count
            print(f"[{current_time}] ✅ {new_orders} nova(s) ordem(ns) enviada(s)!")
            print(f"   Total: {stats['orders_sent']} ordens | Falhas: {stats['orders_failed']}")
            last_order_count = stats['orders_sent']
        
        # Verificar novas posições
        if len(positions) > last_position_count:
            new_positions = len(positions) - last_position_count
            print(f"[{current_time}] 📈 {new_positions} nova(s) posição(ões) aberta(s)!")
            for pos in positions[-new_positions:]:
                print(f"   • {pos['symbol']} | {pos['type']} | Volume: {pos['volume']} | Profit: {pos['profit']:.2f}")
            last_position_count = len(positions)
        
        # Mostrar status a cada 30 segundos
        if int(time.time()) % 30 == 0:
            print(f"[{current_time}] 📊 Status: {len(positions)} posições | {stats['orders_sent']} ordens | Taxa sucesso: {stats['success_rate']:.1f}%")
        
        time.sleep(5)  # Verificar a cada 5 segundos
        
except KeyboardInterrupt:
    print("")
    print("=" * 60)
    print("⏹️  Monitoramento interrompido")
    print("=" * 60)
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
"@

# Salvar script temporário
$tempScript = "monitor_mt5_temp.py"
$monitorScript | Out-File -FilePath $tempScript -Encoding UTF8

Write-ColorOutput "🚀 Iniciando monitoramento..." "Green"
Write-ColorOutput "💡 Pressione Ctrl+C para parar" "Yellow"
Write-Host ""

# Executar monitoramento
try {
    python $tempScript
} catch {
    Write-ColorOutput "❌ Erro ao executar monitoramento: $_" "Red"
} finally {
    # Limpar script temporário
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "🏁 MONITORAMENTO FINALIZADO" "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"

