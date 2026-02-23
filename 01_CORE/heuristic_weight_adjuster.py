import time

class HeuristicWeightAdjuster:
    """
    Ajustador Heuristico de Pesos com 'Dynamic Variance Cap' e 'Execution Score Reward'.
    Em conformidade com a auditoria CQO Tier-0 para Integridade Estatistica.
    """
    def __init__(self, learning_rate=0.001):
        self.weights = {"RSI": 1.0, "MACD": 1.0, "VOL": 1.0, "VWAP": 1.0}
        self.learning_rate = learning_rate
        
        self.last_update_times = {k: time.time() for k in self.weights}
        self.baseline_weights_per_minute = {k: 1.0 for k in self.weights}

    def update_weights_securely(self, instrument: str, execution_score: float, market_toxicity: float):
        """
        Atualiza o peso baseado em Quality Metrics (Slippage/Fill Rate), nao em PnL bruto.
        O cap de variancia encolhe durante panicos de mercado (Dynamic Cap).
        execution_score: 0.0 (Falha total de modelo/slippage) ate 1.0 (Perfeicao)
        market_toxicity: 0.0 (Mercado calmo) ate 1.0 (Black Swan / VIX Extremo)
        """
        current_time = time.time()
        
        # Reset baseline per minute
        if current_time - self.last_update_times[instrument] > 60:
            self.baseline_weights_per_minute[instrument] = self.weights[instrument]
            self.last_update_times[instrument] = current_time

        current_weight = self.weights[instrument]
        baseline = self.baseline_weights_per_minute[instrument]
        
        # 1. REWARD FUNCTION: Execution Quality > PnL
        # Se o score de execucao e alto (1.0), raw_adjustment e positivo. Se o score e baixo, penaliza.
        raw_adjustment = self.learning_rate * (execution_score - 0.5) * 2.0 
        proposed_weight = current_weight + raw_adjustment
        
        # 2. DYNAMIC VARIANCE CAP: Encolhe o limite se a toxicidade do mercado subir
        # Em dias calmos = 5% max variance. Em VIX Extremo (toxicidade=1) = Max 2.5% variance
        dynamic_cap_percentage = 0.05 / (1.0 + market_toxicity)
        
        upper_bound = baseline * (1.0 + dynamic_cap_percentage)
        lower_bound = baseline * (1.0 - dynamic_cap_percentage)
        
        # 3. Apply bounds
        secured_weight = max(lower_bound, min(upper_bound, proposed_weight))
        
        # Global clamp between 0.01 and 2.0
        self.weights[instrument] = max(0.01, min(2.0, secured_weight))
        
        return self.weights[instrument]

if __name__ == "__main__":
    adjuster = HeuristicWeightAdjuster()
    print("[CQO COMPLIANCE] Heuristic Adjuster ativo com Dynamic Variance Cap (Vol-Adjusted) e Execution Score Reward.")
