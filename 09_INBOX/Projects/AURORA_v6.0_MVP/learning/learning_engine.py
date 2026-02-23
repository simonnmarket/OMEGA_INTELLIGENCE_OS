"""
Learning Engine - AURORA v6.0 MVP
Motor de aprendizado contínuo
"""

import os
import pickle
import threading
import time
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("LEARNING_ENGINE")


# Condições para retreino
RETRAIN_CONDITIONS = {
    "new_experiences": 1000,      # Buffer > 1000 novas experiências
    "sharpe_drop": 0.1,           # Sharpe caiu 10%
    "max_drawdown": 0.05,         # DD > 5%
    "hours_since_last": 24        # 24h sem retreino
}


class LearningEngine:
    """
    Motor de Aprendizado Contínuo
    
    Responsabilidades:
    - Verificar condições de retreino periodicamente
    - Retreinar modelos quando necessário
    - Validar novo modelo (backtest 30 dias)
    - Implantar se validação > atual
    - Salvar versões dos modelos
    
    Fluxo:
        1. Experience Buffer → sample(5000)
        2. Train novo modelo
        3. Backtest validation (30 dias histórico)
        4. Compare: novo_sharpe > atual_sharpe?
        5. Se SIM → Deploy (save as model_vX.pkl)
        6. Se NÃO → Log + descarta
    """
    
    def __init__(
        self,
        experience_buffer,
        models_path: str = "data/models/",
        check_interval_seconds: int = 3600  # 1 hora
    ):
        self.buffer = experience_buffer
        self.models_path = models_path
        self.check_interval = check_interval_seconds
        
        self.active = False
        self.thread = None
        self.last_train_time = None
        self.current_model_version = 0
        self.current_sharpe = 0.0
        self.train_count = 0
        
        # Callbacks
        self.on_model_updated: Optional[Callable] = None
        
        # Garantir diretório de modelos
        os.makedirs(models_path, exist_ok=True)
        
    def start(self):
        """Inicia engine em background thread"""
        if self.active:
            return
            
        self.active = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("LearningEngine started (background)")
        
    def stop(self):
        """Para engine"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("LearningEngine stopped")
    
    def _run_loop(self):
        """Loop principal em background"""
        while self.active:
            try:
                should_retrain, reason = self._check_retrain_conditions()
                
                if should_retrain:
                    logger.info(f"Retrain triggered: {reason}")
                    self._retrain_model()
                    
            except Exception as e:
                logger.error(f"Learning loop error: {e}")
            
            # Aguardar próximo check
            time.sleep(self.check_interval)
    
    def _check_retrain_conditions(self) -> tuple:
        """
        Verifica se deve retreinar
        
        Returns:
            (should_retrain: bool, reason: str)
        """
        # 1. Verificar número de experiências
        exp_count = self.buffer.count()
        if exp_count >= RETRAIN_CONDITIONS["new_experiences"]:
            return True, f"Buffer has {exp_count} experiences"
        
        # 2. Verificar tempo desde último treino
        if self.last_train_time:
            hours_elapsed = (datetime.now() - self.last_train_time).total_seconds() / 3600
            if hours_elapsed >= RETRAIN_CONDITIONS["hours_since_last"]:
                return True, f"{hours_elapsed:.1f}h since last train"
        else:
            # Nunca treinou, treinar se tiver dados suficientes
            if exp_count >= 100:
                return True, "Initial training"
        
        return False, "No retrain needed"
    
    def _retrain_model(self):
        """Executa retreino do modelo"""
        logger.info("Starting model retrain...")
        
        try:
            # 1. Sample experiências
            experiences = self.buffer.sample(5000)
            
            if len(experiences) < 100:
                logger.warning("Not enough experiences for training")
                return
            
            # 2. Preparar dados
            states = []
            actions = []
            rewards = []
            
            for state, action, reward, next_state, metadata in experiences:
                if state is not None:
                    states.append(state)
                    actions.append(action)
                    rewards.append(reward)
            
            # 3. Treinar modelo (simplificado - aqui seria o ML real)
            # Em produção, usar ml_models/MetaLearningAdapter.py
            model_data = {
                "states_shape": len(states),
                "avg_reward": sum(rewards) / len(rewards) if rewards else 0,
                "action_distribution": {
                    "BUY": actions.count("BUY"),
                    "SELL": actions.count("SELL"),
                    "HOLD": actions.count("HOLD")
                },
                "trained_at": datetime.now().isoformat()
            }
            
            # 4. Validar modelo (backtest simulado)
            new_sharpe = self._validate_model(model_data)
            
            # 5. Comparar com modelo atual
            if new_sharpe > self.current_sharpe:
                # 6. Deploy novo modelo
                self._deploy_model(model_data, new_sharpe)
                logger.info(f"Model upgraded: Sharpe {self.current_sharpe:.3f} → {new_sharpe:.3f}")
            else:
                logger.info(f"Model discarded: new={new_sharpe:.3f} <= current={self.current_sharpe:.3f}")
            
            self.last_train_time = datetime.now()
            self.train_count += 1
            
        except Exception as e:
            logger.error(f"Retrain failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _validate_model(self, model_data: Dict) -> float:
        """
        Valida modelo com backtest
        
        Args:
            model_data: Dados do modelo treinado
            
        Returns:
            float: Sharpe ratio do modelo
        """
        # Simulação simplificada de validação
        # Em produção, fazer backtest real de 30 dias
        
        avg_reward = model_data.get("avg_reward", 0)
        
        # Sharpe simplificado baseado em rewards
        # Em produção: calcular Sharpe real com retornos
        sharpe = avg_reward * 10  # Escala aproximada
        
        return max(0, sharpe)
    
    def _deploy_model(self, model_data: Dict, sharpe: float):
        """
        Deploy novo modelo
        
        Args:
            model_data: Dados do modelo
            sharpe: Sharpe ratio validado
        """
        self.current_model_version += 1
        self.current_sharpe = sharpe
        
        # Salvar modelo
        model_path = os.path.join(
            self.models_path,
            f"model_v{self.current_model_version}.pkl"
        )
        
        with open(model_path, 'wb') as f:
            pickle.dump({
                "version": self.current_model_version,
                "sharpe": sharpe,
                "data": model_data,
                "deployed_at": datetime.now().isoformat()
            }, f)
        
        logger.info(f"Model deployed: {model_path}")
        
        # Callback
        if self.on_model_updated:
            self.on_model_updated(self.current_model_version, sharpe)
    
    def force_retrain(self):
        """Força retreino imediato"""
        logger.info("Forcing retrain...")
        self._retrain_model()
    
    def get_status(self) -> Dict:
        """Retorna status do engine"""
        return {
            "active": self.active,
            "current_model_version": self.current_model_version,
            "current_sharpe": self.current_sharpe,
            "last_train_time": self.last_train_time.isoformat() if self.last_train_time else None,
            "train_count": self.train_count,
            "buffer_size": self.buffer.count() if self.buffer else 0,
            "retrain_conditions": RETRAIN_CONDITIONS
        }
    
    def load_latest_model(self) -> Optional[Dict]:
        """Carrega modelo mais recente salvo"""
        try:
            models = [f for f in os.listdir(self.models_path) if f.endswith('.pkl')]
            if not models:
                return None
            
            # Pegar mais recente
            latest = sorted(models)[-1]
            path = os.path.join(self.models_path, latest)
            
            with open(path, 'rb') as f:
                model = pickle.load(f)
            
            self.current_model_version = model.get("version", 0)
            self.current_sharpe = model.get("sharpe", 0)
            
            logger.info(f"Loaded model: {latest} (v{self.current_model_version}, sharpe={self.current_sharpe:.3f})")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None

