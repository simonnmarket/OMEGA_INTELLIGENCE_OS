"""
Agent Base - AURORA v6.0 MVP
Classe base para agentes especializados
"""

import os
import pickle
import sqlite3
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger("AGENT_BASE")


class AgentBase(ABC):
    """
    Classe Base para Agentes Especializados
    
    Cada agente possui:
    - Próprio modelo ML (model_{symbol}_vX.pkl)
    - Experience buffer próprio ({symbol}_trades.db)
    - Aprendizado ONLINE a cada trade
    - Evolução de parâmetros a cada N trades
    - Auto-desligamento se Sharpe < threshold
    - Capacidade de transferir conhecimento
    
    Ciclo de Vida:
        Nasce simples → Cresce forte → Evolui sozinho
    """
    
    def __init__(
        self,
        symbol: str,
        data_path: str = "data/agents/",
        min_sharpe: float = 0.0,
        evolution_interval: int = 100
    ):
        self.symbol = symbol
        self.data_path = data_path
        self.min_sharpe = min_sharpe
        self.evolution_interval = evolution_interval
        
        # Estado do agente
        self.active = False
        self.created_at = datetime.now()
        self.trade_count = 0
        self.total_pnl = 0.0
        self.sharpe_ratio = 0.0
        self.win_rate = 0.0
        self.version = 1
        
        # Paths específicos do agente
        self.model_path = os.path.join(data_path, f"model_{symbol.lower()}_v{self.version}.pkl")
        self.db_path = os.path.join(data_path, f"{symbol.lower()}_trades.db")
        
        # Modelo e buffer
        self.model = None
        self.conn = None
        
        # Genoma (parâmetros evolutivos)
        self.genome = self._default_genome()
        
        # Garantir diretórios
        os.makedirs(data_path, exist_ok=True)
        
        # Inicializar
        self._init_database()
        self._load_or_create_model()
        
        logger.info(f"Agent {symbol} initialized (v{self.version})")
    
    def _default_genome(self) -> Dict:
        """Genoma padrão do agente"""
        return {
            "confidence_threshold": 0.6,
            "position_size_factor": 1.0,
            "risk_multiplier": 1.0,
            "learning_rate": 0.001,
            "exploration_rate": 0.1,
            "momentum_weight": 0.5,
            "mean_reversion_weight": 0.3,
            "trend_weight": 0.2
        }
    
    def _init_database(self):
        """Inicializa banco SQLite do agente"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                price FLOAT NOT NULL,
                volume FLOAT NOT NULL,
                pnl FLOAT DEFAULT 0.0,
                confidence FLOAT DEFAULT 0.0,
                state_features BLOB,
                genome_version INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                version INTEGER NOT NULL,
                sharpe_before FLOAT,
                sharpe_after FLOAT,
                genome_changes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def _load_or_create_model(self):
        """Carrega modelo existente ou cria novo"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data.get("model")
                    self.genome = data.get("genome", self.genome)
                    self.version = data.get("version", 1)
                    self.sharpe_ratio = data.get("sharpe", 0.0)
                logger.info(f"Agent {self.symbol} model loaded (v{self.version})")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Cria novo modelo inicial"""
        self.model = {
            "type": "simple_ensemble",
            "weights": np.random.random(10),
            "bias": 0.0,
            "created_at": datetime.now().isoformat()
        }
        self._save_model()
        logger.info(f"Agent {self.symbol} new model created (v{self.version})")
    
    def _save_model(self):
        """Salva modelo atual"""
        self.model_path = os.path.join(
            self.data_path, 
            f"model_{self.symbol.lower()}_v{self.version}.pkl"
        )
        
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                "model": self.model,
                "genome": self.genome,
                "version": self.version,
                "sharpe": self.sharpe_ratio,
                "trade_count": self.trade_count,
                "saved_at": datetime.now().isoformat()
            }, f)
        
        logger.debug(f"Agent {self.symbol} model saved (v{self.version})")
    
    def activate(self):
        """Ativa o agente"""
        self.active = True
        logger.info(f"Agent {self.symbol} ACTIVATED")
    
    def deactivate(self, reason: str = "manual"):
        """Desativa o agente"""
        self.active = False
        logger.warning(f"Agent {self.symbol} DEACTIVATED: {reason}")
    
    def record_trade(
        self,
        action: str,
        price: float,
        volume: float,
        pnl: float,
        confidence: float,
        state_features: np.ndarray = None
    ):
        """Registra trade no buffer do agente"""
        self.conn.execute(
            """
            INSERT INTO trades (timestamp, action, price, volume, pnl, confidence, state_features, genome_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                action,
                price,
                volume,
                pnl,
                confidence,
                pickle.dumps(state_features) if state_features is not None else None,
                self.version
            )
        )
        self.conn.commit()
        
        # Atualizar estatísticas
        self.trade_count += 1
        self.total_pnl += pnl
        
        # Verificar evolução
        if self.trade_count % self.evolution_interval == 0:
            self._evolve()
        
        # Verificar auto-desligamento
        self._check_auto_shutdown()
    
    def _calculate_sharpe(self, lookback: int = 100) -> float:
        """Calcula Sharpe Ratio recente"""
        cursor = self.conn.execute(
            "SELECT pnl FROM trades ORDER BY id DESC LIMIT ?",
            (lookback,)
        )
        pnls = [row[0] for row in cursor.fetchall()]
        
        if len(pnls) < 10:
            return 0.0
        
        returns = np.array(pnls)
        if returns.std() == 0:
            return 0.0
        
        # Sharpe anualizado (assumindo ~252 trades/ano)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        return sharpe
    
    def _check_auto_shutdown(self):
        """Verifica se deve auto-desligar"""
        if self.trade_count < 50:
            return  # Mínimo de trades para avaliar
        
        self.sharpe_ratio = self._calculate_sharpe()
        
        if self.sharpe_ratio < self.min_sharpe:
            self.deactivate(f"Sharpe {self.sharpe_ratio:.2f} < {self.min_sharpe}")
    
    def _evolve(self):
        """Evolui genoma do agente"""
        old_sharpe = self.sharpe_ratio
        
        # Calcular novo sharpe
        new_sharpe = self._calculate_sharpe()
        
        # Ajustar genoma baseado em performance
        changes = {}
        
        if new_sharpe > old_sharpe:
            # Reforçar comportamento atual
            self.genome["confidence_threshold"] *= 0.95
            self.genome["exploration_rate"] *= 0.9
            changes["confidence_threshold"] = "decreased (good performance)"
        else:
            # Aumentar exploração
            self.genome["exploration_rate"] = min(0.3, self.genome["exploration_rate"] * 1.1)
            changes["exploration_rate"] = "increased (exploring)"
        
        # Log evolução
        self.conn.execute(
            """
            INSERT INTO evolution_log (timestamp, version, sharpe_before, sharpe_after, genome_changes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                self.version,
                old_sharpe,
                new_sharpe,
                str(changes)
            )
        )
        self.conn.commit()
        
        # Incrementar versão e salvar
        self.version += 1
        self.sharpe_ratio = new_sharpe
        self._save_model()
        
        logger.info(f"Agent {self.symbol} EVOLVED to v{self.version} (Sharpe: {old_sharpe:.2f} → {new_sharpe:.2f})")
    
    def get_experience_sample(self, n: int = 1000) -> List[Tuple]:
        """Retorna amostra de experiências para transfer learning"""
        cursor = self.conn.execute(
            "SELECT state_features, action, pnl FROM trades WHERE state_features IS NOT NULL ORDER BY RANDOM() LIMIT ?",
            (n,)
        )
        
        results = []
        for row in cursor.fetchall():
            state = pickle.loads(row[0]) if row[0] else None
            action = row[1]
            reward = row[2]
            results.append((state, action, reward))
        
        return results
    
    def receive_knowledge(self, experiences: List[Tuple], source_agent: str):
        """Recebe conhecimento de outro agente (transfer learning)"""
        logger.info(f"Agent {self.symbol} receiving {len(experiences)} experiences from {source_agent}")
        
        # Filtrar e adaptar experiências
        adapted_count = 0
        for state, action, reward in experiences:
            if state is not None and reward > 0:  # Apenas experiências positivas
                # Inserir com marcação de transferência
                self.conn.execute(
                    """
                    INSERT INTO trades (timestamp, action, price, volume, pnl, confidence, state_features, genome_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datetime.now().isoformat(),
                        action,
                        0.0,  # Preço não conhecido
                        0.01,  # Volume mínimo
                        reward * 0.5,  # Reward descontado (não é experiência direta)
                        0.5,  # Confiança média
                        pickle.dumps(state),
                        -1  # Versão -1 indica transferência
                    )
                )
                adapted_count += 1
        
        self.conn.commit()
        logger.info(f"Agent {self.symbol} adapted {adapted_count} experiences")
    
    @abstractmethod
    def generate_signal(self, state: Dict) -> Dict:
        """
        Gera sinal de trading baseado no estado
        
        Args:
            state: Estado atual do mercado
            
        Returns:
            dict: {"action": "BUY|SELL|HOLD", "confidence": 0.0-1.0}
        """
        pass
    
    @abstractmethod
    def learn_online(self, state: Dict, action: str, reward: float, next_state: Dict):
        """
        Aprendizado online a cada trade
        
        Args:
            state: Estado antes da ação
            action: Ação tomada
            reward: Recompensa (P&L)
            next_state: Estado após a ação
        """
        pass
    
    def get_status(self) -> Dict:
        """Retorna status do agente"""
        return {
            "symbol": self.symbol,
            "active": self.active,
            "version": self.version,
            "trade_count": self.trade_count,
            "total_pnl": self.total_pnl,
            "sharpe_ratio": self.sharpe_ratio,
            "genome": self.genome,
            "created_at": self.created_at.isoformat(),
            "model_path": self.model_path
        }
    
    def close(self):
        """Fecha conexões"""
        if self.conn:
            self.conn.close()
        logger.info(f"Agent {self.symbol} closed")

