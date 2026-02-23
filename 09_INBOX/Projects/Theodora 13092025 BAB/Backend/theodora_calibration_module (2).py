import pandas as pd
import numpy as np


class TheodoraCalibrationModule:
    def __init__(self, user_market_references=None):
        # user_market_references: Dicionário com pesos ou prioridades para símbolos/segmentos
        # Ex: {"BTCUSD": 1.2, "EURUSD": 0.8, "ETFs_DEFESA": 1.5}
        self.user_market_references = user_market_references if user_market_references is not None else {}
        self.calibration_history = pd.DataFrame(columns=[
            "timestamp", "symbol", "order_type", "executed_price", "actual_profit",
            "predicted_confidence", "market_regime", "heisenberg_risk", "qft_flow", "fluid_pressure",
            "adjusted_confidence_threshold", "calibration_factor", "trade_successful"
        ])

    def get_market_reference_weight(self, symbol):
        """
        Retorna o peso de referência do usuário para um dado símbolo.
        Pode ser expandido para considerar setores, tipos de ativos, etc.
        """
        # Exemplo simplificado: verifica se o símbolo está nas referências diretas
        # Em um sistema mais complexo, mapearia símbolos para setores/tipos de ativos
        weight = self.user_market_references.get(symbol, 1.0)  # Padrão de 1.0 se não especificado

        # Exemplo de lógica para ETFs de defesa, penny stocks, etc.
        if "ETFS_DEFESA" in self.user_market_references and "ETF" in symbol.upper():
            weight *= self.user_market_references["ETFS_DEFESA"]
        # Adicionar lógica similar para penny stocks, commodities, etc.

        return weight

    def get_performance_feedback(self, symbol=None):
        """
        Obtém feedback de desempenho da calibração para um símbolo específico ou geral.
        """
        filtered_history = self.calibration_history
        if symbol:
            filtered_history = self.calibration_history[self.calibration_history["symbol"] == symbol]

        if filtered_history.empty:
            return {"avg_profit": 0.0, "success_rate": 0.0, "num_trades": 0}

        avg_profit = filtered_history["actual_profit"].mean()
        success_rate = filtered_history["trade_successful"].mean()
        num_trades = len(filtered_history)

        return {"avg_profit": avg_profit, "success_rate": success_rate, "num_trades": num_trades}

    def adjust_ml_agent_calibration(self, current_confidence, symbol, market_regime, heisenberg_risk, qft_flow, fluid_pressure):
        """
        Ajusta a calibração do agente ML/IA com base nas referências do usuário, condições de mercado
        e feedback de desempenho histórico (o "dosador científico").
        Retorna um threshold de confiança ajustado e um fator de calibração.
        """
        base_threshold = 0.6  # Threshold de confiança base

        # Ajuste pelo risco quântico: maior risco = maior confiança exigida
        risk_adjustment = heisenberg_risk * 0.2  # Ex: 0.0 a 0.2

        # Ajuste pelo regime de mercado: maior cautela em mercados não direcionais
        regime_adjustment = 0.0
        if "Consolidação" in market_regime or "Alta Volatilidade" in market_regime:
            regime_adjustment = 0.1  # Exige 10% a mais de confiança em mercados voláteis/indecisos

        # Ajuste pelo fluxo quântico e pressão de mercado
        flow_pressure_adjustment = 0.0
        if qft_flow > 0.7 and fluid_pressure > 0.7:  # Forte sinal de compra
            flow_pressure_adjustment = -0.05
        elif qft_flow < -0.7 and fluid_pressure < -0.7:  # Forte sinal de venda
            flow_pressure_adjustment = -0.05
        elif abs(qft_flow) < 0.3 and abs(fluid_pressure) < 0.3:  # Sinais fracos
            flow_pressure_adjustment = 0.05  # Aumenta o threshold se os sinais quânticos forem fracos

        # Ajuste pelas referências de mercado do usuário
        user_weight = self.get_market_reference_weight(symbol)
        user_adjustment = (1.0 - user_weight) * 0.05  # Ex: se peso 1.2, ajuste -0.01

        # --- Dosador Científico: Ajuste baseado no feedback de desempenho ---
        performance_feedback = self.get_performance_feedback(symbol)
        performance_adjustment = 0.0

        if performance_feedback["num_trades"] > 5:  # Requer um mínimo de trades para calibração
            if performance_feedback["avg_profit"] < 0 and performance_feedback["success_rate"] < 0.5:
                performance_adjustment = 0.1  # Aumenta o threshold se o desempenho for ruim
            elif performance_feedback["avg_profit"] > 0 and performance_feedback["success_rate"] > 0.6:
                performance_adjustment = -0.05  # Diminui o threshold se o desempenho for bom
        # --- Fim Dosador Científico ---

        adjusted_threshold = base_threshold + risk_adjustment + regime_adjustment + flow_pressure_adjustment + user_adjustment + performance_adjustment
        adjusted_threshold = max(0.5, min(0.9, adjusted_threshold))  # Limita o threshold entre 0.5 e 0.9

        calibration_factor = (adjusted_threshold - base_threshold) / base_threshold  # Fator de calibração

        return adjusted_threshold, calibration_factor

    def record_order_calibration(self, timestamp, symbol, order_type, executed_price, actual_profit,
                                 predicted_confidence, market_regime, heisenberg_risk, qft_flow, fluid_pressure,
                                 adjusted_confidence_threshold, calibration_factor):
        """
        Registra os detalhes de uma ordem executada para calibração futura.
        """
        trade_successful = actual_profit > 0  # Define se o trade foi bem-sucedido

        new_entry = {
            "timestamp": timestamp,
            "symbol": symbol,
            "order_type": order_type,
            "executed_price": executed_price,
            "actual_profit": actual_profit,
            "predicted_confidence": predicted_confidence,
            "market_regime": market_regime,
            "heisenberg_risk": heisenberg_risk,
            "qft_flow": qft_flow,
            "fluid_pressure": fluid_pressure,
            "adjusted_confidence_threshold": adjusted_confidence_threshold,
            "calibration_factor": calibration_factor,
            "trade_successful": trade_successful
        }
        self.calibration_history = pd.concat([self.calibration_history, pd.DataFrame([new_entry])], ignore_index=True)

    def get_calibration_report(self):
        """
        Gera um relatório da história de calibração.
        """
        return self.calibration_history

    def analyze_calibration_performance(self):
        """
        Analisa o desempenho da calibração ao longo do tempo.
        Pode identificar se os ajustes estão levando a melhores resultados.
        """
        if self.calibration_history.empty:
            return "Nenhum dado de calibração para analisar."

        # Exemplo de análise: correlação entre fator de calibração e lucro
        analysis = {
            "total_trades": len(self.calibration_history),
            "total_profit": self.calibration_history["actual_profit"].sum(),
            "avg_profit_per_trade": self.calibration_history["actual_profit"].mean(),
            "correlation_calibration_profit": self.calibration_history["calibration_factor"].corr(self.calibration_history["actual_profit"])
        }
        return analysis


if __name__ == "__main__":
    # Exemplo de uso
    user_refs = {"BTCUSD": 1.3, "EURUSD": 0.9, "ETFS_DEFESA": 1.1, "COFFEE": 1.2}
    calibration_module = TheodoraCalibrationModule(user_market_references=user_refs)
    print("THEODORA Calibration Module pronto.")


