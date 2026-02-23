#!/usr/bin/env python3
"""
VERSÃO SIMPLIFICADA - ARCH-001
Execução direta sem travamentos
"""
import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("ARCH-001: CONSOLIDAÇÃO DE EXECUTORES MT5 - AURORA v5.1")
print("=" * 70)

# Fase 1: Identificar executores MT5
print("\n[FASE 1] Identificando executores MT5...")

executores_encontrados = []
padroes_nomes = [
    "mt5_executor", "MT5Executor", "mt5_exec", "MT5_EXEC",
    "MT5NoStopsExecutor", "MT5_STOPS_FIX", "MT5LimitExecutor", "MT5MarketExecutor"
]

for root, dirs, files in os.walk("."):
    # Ignorar diretórios do sistema
    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".idea", "node_modules", "BACKUPS", "backups"]]
    
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            
            # Verificar por nome
            encontrado_nome = any(padrao.lower() in file.lower() for padrao in padroes_nomes)
            
            # Verificar por conteúdo
            encontrado_conteudo = False
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read(5000)
                    encontrado_conteudo = any(p in conteudo for p in ["import MetaTrader5", "import mt5", "mt5.initialize", "mt5.order_send"])
            except:
                continue
            
            if encontrado_nome or encontrado_conteudo:
                info = {
                    "arquivo": file_path,
                    "nome": file,
                    "tamanho_bytes": os.path.getsize(file_path),
                    "encontrado_por": "NOME" if encontrado_nome else "CONTEUDO"
                }
                executores_encontrados.append(info)
                print(f"  ✅ Encontrado: {file_path} ({info['tamanho_bytes']} bytes)")

print(f"\n[RESULTADO] {len(executores_encontrados)} executores encontrados")

# Salvar resultado
resultado = {
    "timestamp": datetime.now().isoformat(),
    "executores_encontrados": executores_encontrados,
    "total": len(executores_encontrados)
}

with open("arch001_resultado_rapido.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"\n✅ Resultado salvo em: arch001_resultado_rapido.json")
print(f"\n📊 RESUMO:")
print(f"   • Executores MT5 encontrados: {len(executores_encontrados)}")
for exec in executores_encontrados:
    print(f"     - {exec['arquivo']}")

if len(executores_encontrados) <= 1:
    print(f"\n✅ Sistema já consolidado - apenas 1 executor encontrado")
else:
    print(f"\n⚠️ {len(executores_encontrados)} executores encontrados - consolidação necessária")

