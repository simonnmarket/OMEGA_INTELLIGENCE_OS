#!/usr/bin/env python3
"""ARCH-001 FASE 1: Identificar Executores MT5"""
import os
import json
from datetime import datetime

print("=" * 70)
print("ARCH-001 FASE 1: IDENTIFICANDO EXECUTORES MT5")
print("=" * 70)

executores_encontrados = []
padroes_nomes = [
    "mt5_executor", "MT5Executor", "mt5_exec", "MT5_EXEC",
    "MT5NoStopsExecutor", "MT5_STOPS_FIX", "MT5LimitExecutor", "MT5MarketExecutor"
]
padroes_conteudo = [
    "import MetaTrader5", "import mt5", "mt5.initialize", 
    "mt5.order_send", "MT5_TIMEOUT", "MT5_DEVIATION"
]

print("\n[1/1] Buscando executores MT5...")

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".idea", "node_modules", "BACKUPS", "backups", "logs_arch001"]]
    
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            
            encontrado_nome = any(padrao.lower() in file.lower() for padrao in padroes_nomes)
            encontrado_conteudo = False
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read(5000)
                    encontrado_conteudo = any(p in conteudo for p in padroes_conteudo)
            except:
                continue
            
            if encontrado_nome or encontrado_conteudo:
                info = {
                    "arquivo": file_path,
                    "nome": file,
                    "diretorio": root,
                    "tamanho_bytes": os.path.getsize(file_path),
                    "encontrado_por": "NOME" if encontrado_nome else "CONTEUDO"
                }
                executores_encontrados.append(info)
                print(f"  ✅ {file_path} ({info['tamanho_bytes']} bytes)")

# Remover duplicatas por caminho
executores_unicos = []
caminhos_vistos = set()
for exec in executores_encontrados:
    if exec["arquivo"] not in caminhos_vistos:
        executores_unicos.append(exec)
        caminhos_vistos.add(exec["arquivo"])

resultado = {
    "timestamp": datetime.now().isoformat(),
    "fase": "FASE_1_IDENTIFICACAO",
    "executores_encontrados": executores_unicos,
    "total": len(executores_unicos)
}

with open("arch001_fase1_resultado.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"\n✅ FASE 1 CONCLUÍDA")
print(f"   • Executores encontrados: {len(executores_unicos)}")
print(f"   • Resultado salvo em: arch001_fase1_resultado.json")

if len(executores_unicos) == 0:
    print(f"\n⚠️ Nenhum executor MT5 encontrado")
elif len(executores_unicos) == 1:
    print(f"\n✅ Sistema já consolidado - apenas 1 executor")
else:
    print(f"\n⚠️ {len(executores_unicos)} executores encontrados - consolidação necessária")

