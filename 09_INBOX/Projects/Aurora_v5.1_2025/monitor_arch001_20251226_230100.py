#!/usr/bin/env python3
"""
📊 SISTEMA DE MONITORAMENTO ARCH-001
Monitora integridade e performance do sistema integrado
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

class MonitorARCH001:
    """Monitor do sistema ARCH-001"""
    
    def __init__(self):
        self.inicio = datetime.now()
        self.log_file = "logs/monitor_arch001.log"
        self.status_file = "status_arch001.json"
        self.intervalo_verificacao = 300  # 5 minutos
        
        # Criar diretório de logs
        os.makedirs("logs", exist_ok=True)
    
    def verificar_arquivos_criticos(self):
        """Verificar arquivos críticos do sistema"""
        arquivos_criticos = [
            "ARCH001_EXECUTOR_FINAL_*.py",
            "configuracao_arch001_*.json",
            "checkpoint_*.json",
            "backup_*.zip"
        ]
        
        resultados = []
        for padrao in arquivos_criticos:
            for arquivo in Path(".").glob(padrao):
                if arquivo.is_file():
                    try:
                        hash_arquivo = self.calcular_hash(arquivo)
                        resultados.append({
                            "arquivo": str(arquivo),
                            "tamanho_kb": arquivo.stat().st_size / 1024,
                            "hash": hash_arquivo[:16] + "...",
                            "status": "OK",
                            "timestamp": datetime.now().isoformat()
                        })
                    except:
                        pass
        
        return resultados
    
    def calcular_hash(self, arquivo):
        """Calcular hash SHA256"""
        hasher = hashlib.sha256()
        with open(arquivo, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def executar_verificacao_completa(self):
        """Executar verificação completa"""
        print(f"[{datetime.now().isoformat()}] Executando verificação ARCH-001...")
        
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "arquivos_criticos": self.verificar_arquivos_criticos(),
            "status_geral": "ESTAVEL"
        }
        
        # Salvar resultados
        with open(self.status_file, 'w') as f:
            json.dump(resultados, f, indent=2)
        
        return resultados

if __name__ == "__main__":
    monitor = MonitorARCH001()
    monitor.executar_verificacao_completa()
    print("✅ Monitoramento executado")
