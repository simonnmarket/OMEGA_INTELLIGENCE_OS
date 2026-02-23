"""
Agent Orchestrator - AURORA v6.0 MVP
Maestro dos agentes especializados
"""

import threading
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .agent_base import AgentBase
from .agent_xauusd import XAUUSDAgent
from .agent_eurusd import EURUSDAgent

logger = logging.getLogger("AGENT_ORCHESTRATOR")


class AgentOrchestrator:
    """
    Maestro dos Agentes Especializados
    
    Responsabilidades:
    - Monitorar todos os agentes a cada minuto
    - Identificar qual agente está performando melhor
    - Aumentar alocação para agentes lucrativos
    - Desativar agentes com Sharpe negativo
    - Orquestrar transferência de conhecimento entre agentes
    
    Fluxo:
        1. Monitor loop (1 min)
        2. Coletar métricas de cada agente
        3. Ajustar alocações
        4. Transferir conhecimento
        5. Ativar/desativar agentes
    """
    
    def __init__(
        self,
        data_path: str = "data/agents/",
        monitor_interval: int = 60,  # segundos
        min_sharpe_threshold: float = 0.0,
        transfer_threshold: float = 0.5  # Sharpe mínimo para ser fonte
    ):
        self.data_path = data_path
        self.monitor_interval = monitor_interval
        self.min_sharpe = min_sharpe_threshold
        self.transfer_threshold = transfer_threshold
        
        # Agentes gerenciados
        self.agents: Dict[str, AgentBase] = {}
        
        # Alocações (soma = 1.0)
        self.allocations: Dict[str, float] = {}
        
        # Estado
        self.active = False
        self.thread = None
        self.last_monitor = None
        self.monitor_count = 0
        
        # Histórico
        self.performance_history: List[Dict] = []
        
    def register_agent(self, agent: AgentBase):
        """Registra agente no orquestrador"""
        symbol = agent.symbol
        self.agents[symbol] = agent
        self.allocations[symbol] = 1.0 / len(self.agents)  # Igual inicialmente
        
        # Rebalancear alocações
        self._rebalance_allocations()
        
        logger.info(f"Agent {symbol} registered (allocation: {self.allocations[symbol]:.2%})")
    
    def unregister_agent(self, symbol: str):
        """Remove agente do orquestrador"""
        if symbol in self.agents:
            self.agents[symbol].close()
            del self.agents[symbol]
            del self.allocations[symbol]
            self._rebalance_allocations()
            logger.info(f"Agent {symbol} unregistered")
    
    def _rebalance_allocations(self):
        """Rebalanceia alocações para somar 1.0"""
        if not self.allocations:
            return
        
        total = sum(self.allocations.values())
        if total > 0:
            for symbol in self.allocations:
                self.allocations[symbol] /= total
    
    def start(self):
        """Inicia orquestrador em background"""
        if self.active:
            return
        
        self.active = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        # Ativar todos os agentes
        for agent in self.agents.values():
            agent.activate()
        
        logger.info(f"AgentOrchestrator started with {len(self.agents)} agents")
    
    def stop(self):
        """Para orquestrador"""
        self.active = False
        
        for agent in self.agents.values():
            agent.deactivate("orchestrator stopped")
            agent.close()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("AgentOrchestrator stopped")
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.active:
            try:
                self._monitor_cycle()
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            time.sleep(self.monitor_interval)
    
    def _monitor_cycle(self):
        """Executa um ciclo de monitoramento"""
        self.monitor_count += 1
        self.last_monitor = datetime.now()
        
        # 1. Coletar métricas
        metrics = {}
        for symbol, agent in self.agents.items():
            metrics[symbol] = {
                "sharpe": agent.sharpe_ratio,
                "trade_count": agent.trade_count,
                "total_pnl": agent.total_pnl,
                "active": agent.active,
                "version": agent.version
            }
        
        # 2. Identificar melhor e pior
        active_agents = {s: m for s, m in metrics.items() if m["active"]}
        
        if active_agents:
            best_symbol = max(active_agents, key=lambda s: active_agents[s]["sharpe"])
            worst_symbol = min(active_agents, key=lambda s: active_agents[s]["sharpe"])
            
            best_sharpe = active_agents[best_symbol]["sharpe"]
            worst_sharpe = active_agents[worst_symbol]["sharpe"]
            
            # 3. Ajustar alocações
            self._adjust_allocations(metrics)
            
            # 4. Transferir conhecimento (do melhor para os outros)
            if best_sharpe >= self.transfer_threshold:
                self._transfer_knowledge(best_symbol)
            
            # 5. Desativar agentes ruins
            for symbol, m in metrics.items():
                if m["sharpe"] < self.min_sharpe and m["trade_count"] >= 50:
                    self.agents[symbol].deactivate(f"Sharpe {m['sharpe']:.2f} < {self.min_sharpe}")
        
        # 6. Log
        self.performance_history.append({
            "timestamp": self.last_monitor.isoformat(),
            "metrics": metrics,
            "allocations": dict(self.allocations)
        })
        
        # Manter histórico limitado
        if len(self.performance_history) > 1440:  # 24h de dados (1 por minuto)
            self.performance_history = self.performance_history[-1440:]
        
        logger.debug(f"Monitor cycle {self.monitor_count}: {len(active_agents)} active agents")
    
    def _adjust_allocations(self, metrics: Dict):
        """
        Ajusta alocações baseado em performance
        
        Fórmula: allocation = softmax(sharpe_ratios)
        """
        sharpes = {}
        for symbol, m in metrics.items():
            if m["active"]:
                # Sharpe com floor para evitar negativos extremos
                sharpes[symbol] = max(m["sharpe"], -1.0)
        
        if not sharpes:
            return
        
        # Softmax
        import numpy as np
        values = np.array(list(sharpes.values()))
        exp_values = np.exp(values - np.max(values))  # Estabilidade numérica
        softmax = exp_values / exp_values.sum()
        
        for i, symbol in enumerate(sharpes.keys()):
            old_alloc = self.allocations.get(symbol, 0)
            new_alloc = softmax[i]
            
            # Suavizar mudanças (80% antigo + 20% novo)
            self.allocations[symbol] = 0.8 * old_alloc + 0.2 * new_alloc
        
        # Zerar alocação de inativos
        for symbol in self.allocations:
            if symbol not in sharpes:
                self.allocations[symbol] = 0.0
        
        self._rebalance_allocations()
    
    def _transfer_knowledge(self, source_symbol: str):
        """
        Transfere conhecimento do agente fonte para os outros
        """
        source = self.agents.get(source_symbol)
        if not source:
            return
        
        # Obter experiências positivas
        experiences = source.get_experience_sample(500)
        
        if not experiences:
            return
        
        # Transferir para outros agentes
        for symbol, agent in self.agents.items():
            if symbol != source_symbol and agent.active:
                agent.receive_knowledge(experiences, source_symbol)
        
        logger.info(f"Knowledge transferred from {source_symbol} to {len(self.agents)-1} agents")
    
    def get_signal(self, symbol: str, state: Dict) -> Optional[Dict]:
        """
        Obtém sinal do agente específico
        
        Args:
            symbol: Símbolo do ativo
            state: Estado do mercado
            
        Returns:
            Sinal do agente ou None
        """
        agent = self.agents.get(symbol)
        if agent and agent.active:
            signal = agent.generate_signal(state)
            signal["allocation"] = self.allocations.get(symbol, 0)
            return signal
        return None
    
    def report_trade_result(self, symbol: str, state: Dict, action: str, reward: float, next_state: Dict):
        """
        Reporta resultado de trade para aprendizado
        """
        agent = self.agents.get(symbol)
        if agent:
            agent.learn_online(state, action, reward, next_state)
    
    def get_best_agent(self) -> Optional[str]:
        """Retorna símbolo do melhor agente ativo"""
        active = {s: a for s, a in self.agents.items() if a.active}
        if not active:
            return None
        return max(active, key=lambda s: active[s].sharpe_ratio)
    
    def get_status(self) -> Dict:
        """Retorna status do orquestrador"""
        return {
            "active": self.active,
            "agents_count": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "monitor_count": self.monitor_count,
            "last_monitor": self.last_monitor.isoformat() if self.last_monitor else None,
            "allocations": dict(self.allocations),
            "agents": {s: a.get_status() for s, a in self.agents.items()},
            "best_agent": self.get_best_agent()
        }
    
    def create_default_agents(self):
        """Cria e registra agentes padrão (XAUUSD e EURUSD)"""
        xau = XAUUSDAgent(self.data_path)
        eur = EURUSDAgent(self.data_path)
        
        self.register_agent(xau)
        self.register_agent(eur)
        
        logger.info("Default agents created: XAUUSD, EURUSD")

