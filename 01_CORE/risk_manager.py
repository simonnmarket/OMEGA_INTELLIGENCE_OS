class RiskManager:
    """
    Gestor de Risco (Ex-NumeiaTreasury) com 'Cross-Hub Correlation Monitor'
    e 'Latency Kill-Switch'. Exigencias finais do CQO Tier-0 resolvidas.
    """
    def __init__(self, global_aum: float):
        self.global_aum = global_aum
        self.active_hubs = ["FOREX", "CRYPTO", "METALS"]
        self.base_hub_allocation = 0.10 # 10% base per hub
        self.global_systemic_exposure_limit = 0.20 # CQO Limit: Max 20% AUM exposed globally

    def calculate_global_margin_allocation(
        self, 
        hub_toxicities: dict, 
        global_correlation: float,
        crypto_latency_p99_ms: float = 0.0 # Latency Feed from ZeroMQ
    ) -> dict:
        """
        Calcula as margens dinamicamente.
        - Se o mercado global despencar junto (Correlation > 0.7), amassa as alocacoes.
        - Se a latencia da corretora no Hub Crypto superar 50ms, zera o capital do BTC na mesma hora.
        """
        allocated_margins = {}
        total_requested = 0.0
        
        # 1. LATENCY KILL-SWITCH (CQO Mandate)
        # HFT nao tolera > 50ms de lag. Risco de the-fly slippage massivo.
        crypto_blocked = False
        if crypto_latency_p99_ms > 50.0:
            crypto_blocked = True
            print(f"[Risco CQO] LATENCY KILL-SWITCH ATIVADO! Hub Crypto cortado. Ping: {crypto_latency_p99_ms}ms")
        
        # 2. Calcula os pedidos de sobrevivencia
        for hub in self.active_hubs:
            if hub == "CRYPTO" and crypto_blocked:
                # Alocacao zero matematica
                allocated_margins[hub] = 0.0
                continue
                
            toxicity = hub_toxicities.get(hub, 1.0) # Sem dado = medo total
            safe_multiplier = max(0.0, 1.0 - toxicity)
            requested_margin = (self.global_aum * self.base_hub_allocation) * safe_multiplier
            total_requested += requested_margin
            allocated_margins[hub] = requested_margin
            
        # 3. GLOBAL CORRELATION MATRIX (CQO Systemic Shield)
        max_allowed_global_usd = self.global_aum * self.global_systemic_exposure_limit
        
        correlation_penalty_factor = 1.0
        if global_correlation > 0.7:
             correlation_penalty_factor = max(0.1, 1.0 - (global_correlation * 0.5))
             
        final_allocated = {}
        final_total = 0.0
        
        for hub, margin in allocated_margins.items():
            penalized_margin = margin * correlation_penalty_factor
            final_allocated[hub] = penalized_margin
            final_total += penalized_margin
            
        # Hard cap final absoluto limitando aos 20% do fundo global (Morte Sistêmica)
        if final_total > max_allowed_global_usd:
            reduction_ratio = max_allowed_global_usd / final_total
            for hub in final_allocated:
                final_allocated[hub] *= reduction_ratio
                
        return final_allocated

if __name__ == "__main__":
    rm = RiskManager(10000.0)
    print("[CQO COMPLIANCE] Motor de Risco Online.")
    
    # Teste de Stress
    margins = rm.calculate_global_margin_allocation(
        hub_toxicities={"FOREX": 0.5, "CRYPTO": 0.2, "METALS": 0.3},
        global_correlation=0.2,      # Mercado calmo
        crypto_latency_p99_ms=65.0   # Servidor da Binance/MT5 lagging = 65ms
    )
    print(f"Alocacao Teste Latency Kill-Switch: {margins}")
