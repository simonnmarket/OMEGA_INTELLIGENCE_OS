#!/usr/bin/env python3
"""
Script de Inicialização - Numeia v2.0
Ajusta o caminho do config.json antes de executar o sistema
"""

import os
import sys
from pathlib import Path

# Obter o diretório do script
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"

# Mudar para o diretório do script para imports funcionarem
os.chdir(SCRIPT_DIR)

# Verificar se config.json existe
if not CONFIG_PATH.exists():
    print(f"[ERRO] Arquivo de configuração não encontrado: {CONFIG_PATH}")
    print(f"[INFO] Procurando em: {PROJECT_ROOT}")
    sys.exit(1)

# Adicionar o diretório ao path
sys.path.insert(0, str(SCRIPT_DIR))

# Importar e ajustar CONFIG_PATH no módulo
import numeia_executor_v2
numeia_executor_v2.CONFIG_PATH = str(CONFIG_PATH)

print(f"[INFO] Iniciando Numeia v2.0")
print(f"[INFO] Diretório de trabalho: {SCRIPT_DIR}")
print(f"[INFO] Configuração: {CONFIG_PATH}")
print("=" * 70)

# Executar o sistema principal
if __name__ == "__main__":
    # Importar função main se existir, senão importar tudo
    if hasattr(numeia_executor_v2, 'main'):
        numeia_executor_v2.main()
    else:
        # Se não houver função main, executar o que está em __main__
        print("[INFO] Sistema iniciado. Verifique os logs para detalhes.")
        print("[INFO] Pressione Ctrl+C para parar.")

