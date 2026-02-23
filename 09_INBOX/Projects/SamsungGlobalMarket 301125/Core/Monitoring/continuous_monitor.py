#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR CONTÍNUO - COLETA DE DADOS 24/7
PROJETO: Prometheus v3.0.0
PROTOCOLO: Omega TIER-0

Monitora sistema continuamente e gera relatórios periódicos.
"""

import time
import json
from pathlib import Path
from datetime import datetime
from analytics_engine import AnalyticsEngine

def continuous_monitor(interval_minutes=10, output_file="logs/metrics_history.json"):
    """Monitora sistema continuamente"""
    engine = AnalyticsEngine()
    output_path = Path(output_file)
    
    # Criar arquivo de histórico se não existir
    if not output_path.exists():
        history = []
    else:
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    print("=" * 80)
    print("MONITOR CONTÍNUO - SAMSUNG GLOBAL MARKET")
    print("=" * 80)
    print(f"Intervalo: {interval_minutes} minutos")
    print(f"Arquivo de histórico: {output_file}")
    print("Pressione Ctrl+C para parar")
    print("=" * 80)
    print()
    
    try:
        while True:
            # Atualizar métricas
            report = engine.get_kpi_report()
            signal_analysis = engine.get_signal_analysis()
            
            # Adicionar ao histórico
            history.append({
                'timestamp': report['timestamp'],
                'metrics': report['metrics'],
                'kpis': report['kpis'],
                'signal_analysis': signal_analysis
            })
            
            # Manter apenas últimas 1000 entradas
            if len(history) > 1000:
                history = history[-1000:]
            
            # Salvar histórico
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            # Imprimir relatório
            engine.print_report()
            
            # Aguardar próximo ciclo
            print(f"\nPróxima atualização em {interval_minutes} minutos...\n")
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print("\n\nMonitoramento interrompido.")
        print(f"Histórico salvo em: {output_file}")

if __name__ == "__main__":
    import sys
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    continuous_monitor(interval_minutes=interval)

