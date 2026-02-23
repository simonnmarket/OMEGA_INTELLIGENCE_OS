#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYTICS ENGINE - SISTEMA DE ANÁLISE QUANTITATIVA
PROJETO: Prometheus v3.0.0
PROTOCOLO: Omega TIER-0

Coleta e analisa métricas em tempo real:
- Signal-to-Execution Ratio
- Execution Latency
- P&L Simulado (Paper Trading)
- KPIs de Performance
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================
@dataclass
class SignalData:
    """Dados de um sinal gerado"""
    signal_id: str
    timestamp: datetime
    asset: str
    action: str
    confidence: float
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    source: str = "numeia"

@dataclass
class ExecutionData:
    """Dados de uma execução"""
    signal_id: str
    timestamp: datetime
    status: str
    order_ticket: int
    execution_latency_ms: Optional[float] = None

@dataclass
class Metrics:
    """Métricas consolidadas"""
    signals_generated: int = 0
    signals_received_by_ea: int = 0
    signals_executed: int = 0
    signals_rejected: int = 0
    signal_to_execution_ratio: float = 0.0
    avg_execution_latency_ms: float = 0.0
    total_heartbeats: int = 0
    connection_uptime_seconds: float = 0.0
    errors_count: int = 0

# ============================================================================
# PARSER DE LOGS
# ============================================================================
class LogParser:
    """Extrai dados dos logs do servidor"""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.signals: List[SignalData] = []
        self.executions: List[ExecutionData] = []
        self.heartbeats: List[datetime] = []
        self.errors: List[Dict] = []
        
    def parse_server_log(self) -> Tuple[List[SignalData], List[ExecutionData], List[datetime], List[Dict]]:
        """Parseia log do servidor principal"""
        if not self.log_file.exists():
            return [], [], [], []
        
        signals = []
        executions = []
        heartbeats = []
        errors = []
        
        # Padrões regex
        signal_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| TradingEngine\s+\| INFO\s+\| 📡 ALPHA GERADO: (.+?)\n'
            r'.*?Asset: (.+?)\s+\|\s+Action: (.+?)\n'
            r'.*?Confidence: ([\d.]+)%'
        )
        
        execution_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| SocketService\s+\| INFO\s+\| \[RELATORIO\] Signal (.+?): (.+?) \(Order #(\d+)\)'
        )
        
        heartbeat_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| SocketService\s+\| INFO\s+\| \[HEARTBEAT\] Enviado para'
        )
        
        error_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| .+ \| ERROR\s+\| (.+)'
        )
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsear sinais
            for match in signal_pattern.finditer(content):
                timestamp_str, signal_id, asset, action, confidence = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                signals.append(SignalData(
                    signal_id=signal_id.strip(),
                    timestamp=timestamp,
                    asset=asset.strip(),
                    action=action.strip(),
                    confidence=float(confidence) / 100.0,
                    volume=0.01,  # Valor padrão, pode ser extraído se disponível
                    source='numeia'
                ))
            
            # Parsear execuções
            for match in execution_pattern.finditer(content):
                timestamp_str, signal_id, status, order_ticket = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                executions.append(ExecutionData(
                    signal_id=signal_id.strip(),
                    timestamp=timestamp,
                    status=status.strip(),
                    order_ticket=int(order_ticket)
                ))
            
            # Parsear heartbeats
            for match in heartbeat_pattern.finditer(content):
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                heartbeats.append(timestamp)
            
            # Parsear erros
            for match in error_pattern.finditer(content):
                timestamp_str, error_msg = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                errors.append({
                    'timestamp': timestamp,
                    'message': error_msg.strip()
                })
            
        except Exception as e:
            print(f"[ERRO] Falha ao parsear log: {e}")
        
        return signals, executions, heartbeats, errors
    
    def calculate_execution_latency(self, signals: List[SignalData], 
                                   executions: List[ExecutionData]) -> List[float]:
        """Calcula latência de execução para cada sinal executado"""
        latencies = []
        
        # Criar dict de sinais por ID para lookup rápido
        signals_dict = {s.signal_id: s for s in signals}
        
        for execution in executions:
            if execution.signal_id in signals_dict:
                signal = signals_dict[execution.signal_id]
                latency_ms = (execution.timestamp - signal.timestamp).total_seconds() * 1000
                latencies.append(latency_ms)
                execution.execution_latency_ms = latency_ms
        
        return latencies

# ============================================================================
# ANALYTICS ENGINE
# ============================================================================
class AnalyticsEngine:
    """Motor de análise e geração de métricas"""
    
    def __init__(self, log_file: str = "logs/main_server.log"):
        self.log_file = log_file
        self.parser = LogParser(log_file)
        self.metrics = Metrics()
        
    def update_metrics(self):
        """Atualiza métricas a partir dos logs"""
        signals, executions, heartbeats, errors = self.parser.parse_server_log()
        
        # Calcular latências
        latencies = self.parser.calculate_execution_latency(signals, executions)
        
        # Atualizar métricas
        self.metrics.signals_generated = len(signals)
        self.metrics.signals_executed = len([e for e in executions if e.status == "FILLED"])
        self.metrics.signals_rejected = len([e for e in executions if e.status == "REJECTED"])
        self.metrics.total_heartbeats = len(heartbeats)
        self.metrics.errors_count = len(errors)
        
        # Signal-to-execution ratio
        if self.metrics.signals_generated > 0:
            # Assumindo que se há execution report, o EA recebeu o sinal
            self.metrics.signals_received_by_ea = len(executions)
            self.metrics.signal_to_execution_ratio = (
                self.metrics.signals_received_by_ea / self.metrics.signals_generated * 100
            )
        
        # Latência média
        if latencies:
            self.metrics.avg_execution_latency_ms = sum(latencies) / len(latencies)
        
        # Uptime (estimado pela primeira e última entrada de log)
        if signals:
            first_signal = min(s.timestamp for s in signals)
            last_signal = max(s.timestamp for s in signals)
            self.metrics.connection_uptime_seconds = (last_signal - first_signal).total_seconds()
    
    def get_kpi_report(self) -> Dict:
        """Gera relatório de KPIs"""
        self.update_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'signals_generated': self.metrics.signals_generated,
                'signals_received_by_ea': self.metrics.signals_received_by_ea,
                'signals_executed': self.metrics.signals_executed,
                'signals_rejected': self.metrics.signals_rejected,
                'signal_to_execution_ratio_percent': round(self.metrics.signal_to_execution_ratio, 2),
                'avg_execution_latency_ms': round(self.metrics.avg_execution_latency_ms, 2),
                'total_heartbeats': self.metrics.total_heartbeats,
                'connection_uptime_hours': round(self.metrics.connection_uptime_seconds / 3600, 2),
                'errors_count': self.metrics.errors_count,
                'error_rate_percent': round(
                    (self.metrics.errors_count / max(self.metrics.signals_generated, 1)) * 100, 2
                )
            },
            'kpis': {
                'signal_to_execution_target': 95.0,
                'signal_to_execution_status': 'PASS' if self.metrics.signal_to_execution_ratio >= 95.0 else 'FAIL',
                'execution_latency_target_ms': 500.0,
                'execution_latency_status': 'PASS' if self.metrics.avg_execution_latency_ms <= 500.0 else 'FAIL',
                'error_rate_target_percent': 1.0,
                'error_rate_status': 'PASS' if (self.metrics.errors_count / max(self.metrics.signals_generated, 1) * 100) <= 1.0 else 'FAIL'
            }
        }
    
    def get_signal_analysis(self) -> Dict:
        """Analisa padrões nos sinais gerados"""
        signals, _, _, _ = self.parser.parse_server_log()
        
        if not signals:
            return {}
        
        # Análise por asset
        asset_counts = defaultdict(int)
        action_counts = defaultdict(int)
        confidence_values = []
        
        for signal in signals:
            asset_counts[signal.asset] += 1
            action_counts[signal.action] += 1
            confidence_values.append(signal.confidence)
        
        return {
            'total_signals': len(signals),
            'signals_per_hour': len(signals) / max((datetime.now() - signals[0].timestamp).total_seconds() / 3600, 0.1),
            'assets': dict(asset_counts),
            'actions_distribution': dict(action_counts),
            'avg_confidence': sum(confidence_values) / len(confidence_values) if confidence_values else 0.0,
            'min_confidence': min(confidence_values) if confidence_values else 0.0,
            'max_confidence': max(confidence_values) if confidence_values else 0.0,
            'most_active_asset': max(asset_counts.items(), key=lambda x: x[1])[0] if asset_counts else None,
            'dominant_action': max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None
        }
    
    def print_report(self):
        """Imprime relatório formatado"""
        kpi_report = self.get_kpi_report()
        signal_analysis = self.get_signal_analysis()
        
        print("=" * 80)
        print("RELATÓRIO DE KPIs - SAMSUNG GLOBAL MARKET")
        print("=" * 80)
        print(f"Timestamp: {kpi_report['timestamp']}")
        print()
        
        print("MÉTRICAS OPERACIONAIS:")
        print("-" * 80)
        metrics = kpi_report['metrics']
        print(f"  Sinais Gerados: {metrics['signals_generated']}")
        print(f"  Sinais Recebidos pelo EA: {metrics['signals_received_by_ea']}")
        print(f"  Sinais Executados: {metrics['signals_executed']}")
        print(f"  Sinais Rejeitados: {metrics['signals_rejected']}")
        print(f"  Heartbeats: {metrics['total_heartbeats']}")
        print(f"  Uptime: {metrics['connection_uptime_hours']:.2f} horas")
        print(f"  Erros: {metrics['errors_count']}")
        print()
        
        print("KPIs DE PERFORMANCE:")
        print("-" * 80)
        kpis = kpi_report['kpis']
        ratio_status = "[OK]" if kpis['signal_to_execution_status'] == 'PASS' else "[FAIL]"
        latency_status = "[OK]" if kpis['execution_latency_status'] == 'PASS' else "[FAIL]"
        error_status = "[OK]" if kpis['error_rate_status'] == 'PASS' else "[FAIL]"
        
        print(f"  Signal-to-Execution Ratio: {metrics['signal_to_execution_ratio_percent']:.2f}% "
              f"(Meta: >{kpis['signal_to_execution_target']}%) {ratio_status}")
        print(f"  Latência Média: {metrics['avg_execution_latency_ms']:.2f}ms "
              f"(Meta: <{kpis['execution_latency_target_ms']}ms) {latency_status}")
        print(f"  Taxa de Erro: {metrics['error_rate_percent']:.2f}% "
              f"(Meta: <{kpis['error_rate_target_percent']}%) {error_status}")
        print()
        
        if signal_analysis:
            print("ANÁLISE DE SINAIS:")
            print("-" * 80)
            print(f"  Total de Sinais: {signal_analysis['total_signals']}")
            print(f"  Sinais/Hora: {signal_analysis['signals_per_hour']:.2f}")
            print(f"  Asset Mais Ativo: {signal_analysis.get('most_active_asset', 'N/A')}")
            print(f"  Ação Dominante: {signal_analysis.get('dominant_action', 'N/A')}")
            print(f"  Confiança Média: {signal_analysis.get('avg_confidence', 0):.2%}")
            print(f"  Confiança Min/Max: {signal_analysis.get('min_confidence', 0):.2%} / "
                  f"{signal_analysis.get('max_confidence', 0):.2%}")
            
            if signal_analysis.get('assets'):
                print(f"  Distribuição por Asset: {signal_analysis['assets']}")
            if signal_analysis.get('actions_distribution'):
                print(f"  Distribuição por Ação: {signal_analysis['actions_distribution']}")
        
        print()
        print("=" * 80)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import sys
    
    log_file = sys.argv[1] if len(sys.argv) > 1 else "logs/main_server.log"
    
    engine = AnalyticsEngine(log_file)
    engine.print_report()

