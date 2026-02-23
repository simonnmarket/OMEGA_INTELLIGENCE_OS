"""
Experience Buffer - AURORA v6.0 MVP
Armazena experiências de trading para aprendizado
"""

import sqlite3
import pickle
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger("EXPERIENCE_BUFFER")


class ExperienceBuffer:
    """
    Buffer de Experiências para Reinforcement Learning
    
    Responsabilidades:
    - Salvar cada trade como experiência (state, action, reward, next_state)
    - Armazenar em SQLite para persistência
    - Permitir sampling para treino de modelos
    
    Schema SQLite:
        id: INTEGER PRIMARY KEY
        timestamp: TEXT
        symbol: TEXT
        state_features: BLOB (pickle numpy array)
        action: TEXT (BUY/SELL/HOLD)
        reward: FLOAT (P&L normalizado)
        next_state_features: BLOB
        metadata: TEXT (JSON)
    """
    
    def __init__(self, db_path: str = "data/experience_buffer/trades.db"):
        self.db_path = db_path
        self.conn = None
        self._ensure_db()
        
    def _ensure_db(self):
        """Cria banco e tabela se não existir"""
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                state_features BLOB,
                action TEXT NOT NULL,
                reward FLOAT DEFAULT 0.0,
                next_state_features BLOB,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para queries eficientes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON experiences(timestamp)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON experiences(symbol)")
        
        self.conn.commit()
        logger.info(f"ExperienceBuffer initialized: {self.db_path}")
    
    def add(
        self,
        state: any,
        action: str,
        reward: float,
        next_state: any = None,
        symbol: str = "UNKNOWN",
        metadata: Dict = None
    ) -> int:
        """
        Adiciona uma experiência ao buffer
        
        Args:
            state: Features do estado atual (numpy array ou dict)
            action: Ação tomada (BUY/SELL/HOLD)
            reward: Recompensa (P&L normalizado)
            next_state: Features do próximo estado
            symbol: Símbolo do ativo
            metadata: Dados adicionais (JSON)
            
        Returns:
            int: ID da experiência inserida
        """
        cursor = self.conn.execute(
            """
            INSERT INTO experiences 
            (timestamp, symbol, state_features, action, reward, next_state_features, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                symbol,
                pickle.dumps(state),
                action,
                reward,
                pickle.dumps(next_state) if next_state is not None else None,
                json.dumps(metadata) if metadata else None
            )
        )
        
        self.conn.commit()
        exp_id = cursor.lastrowid
        
        logger.debug(f"Experience added: id={exp_id}, action={action}, reward={reward:.4f}")
        return exp_id
    
    def sample(self, batch_size: int = 128) -> List[Tuple]:
        """
        Amostra aleatória de experiências para treino
        
        Args:
            batch_size: Número de experiências a amostrar
            
        Returns:
            List[Tuple]: [(state, action, reward, next_state, metadata), ...]
        """
        cursor = self.conn.execute(
            """
            SELECT state_features, action, reward, next_state_features, metadata
            FROM experiences
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (batch_size,)
        )
        
        results = []
        for row in cursor.fetchall():
            state = pickle.loads(row[0]) if row[0] else None
            action = row[1]
            reward = row[2]
            next_state = pickle.loads(row[3]) if row[3] else None
            metadata = json.loads(row[4]) if row[4] else {}
            
            results.append((state, action, reward, next_state, metadata))
        
        logger.debug(f"Sampled {len(results)} experiences")
        return results
    
    def get_last_n(self, n: int = 1000) -> List[Tuple]:
        """
        Retorna as últimas N experiências
        
        Args:
            n: Número de experiências
            
        Returns:
            List[Tuple]: Últimas N experiências
        """
        cursor = self.conn.execute(
            """
            SELECT state_features, action, reward, next_state_features, metadata
            FROM experiences
            ORDER BY id DESC
            LIMIT ?
            """,
            (n,)
        )
        
        results = []
        for row in cursor.fetchall():
            state = pickle.loads(row[0]) if row[0] else None
            action = row[1]
            reward = row[2]
            next_state = pickle.loads(row[3]) if row[3] else None
            metadata = json.loads(row[4]) if row[4] else {}
            
            results.append((state, action, reward, next_state, metadata))
        
        return results
    
    def clear_old(self, days: int = 90):
        """
        Remove experiências mais antigas que X dias
        
        Args:
            days: Número de dias para manter
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = self.conn.execute(
            "DELETE FROM experiences WHERE timestamp < ?",
            (cutoff,)
        )
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        logger.info(f"Cleared {deleted} old experiences (older than {days} days)")
        return deleted
    
    def count(self) -> int:
        """Retorna número total de experiências"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM experiences")
        return cursor.fetchone()[0]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do buffer"""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(reward) as avg_reward,
                MIN(reward) as min_reward,
                MAX(reward) as max_reward,
                MIN(timestamp) as oldest,
                MAX(timestamp) as newest
            FROM experiences
        """)
        
        row = cursor.fetchone()
        
        # Contagem por ação
        cursor2 = self.conn.execute("""
            SELECT action, COUNT(*) 
            FROM experiences 
            GROUP BY action
        """)
        actions = dict(cursor2.fetchall())
        
        return {
            "total_experiences": row[0],
            "avg_reward": row[1],
            "min_reward": row[2],
            "max_reward": row[3],
            "oldest": row[4],
            "newest": row[5],
            "actions": actions
        }
    
    def close(self):
        """Fecha conexão com banco"""
        if self.conn:
            self.conn.close()
            logger.info("ExperienceBuffer closed")

