# -*- coding: utf-8 -*-
"""
SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0
DIRETIVA FINAL DE EXECUÇÃO: PIVÔ CIENTÍFICO E VALIDAÇÃO DE EDGE

Versão: 1.0 - Diretiva Final e Autoritária
Data: 17 de Novembro de 2025 (CET/Berlin)
Autores: CEO-Cientista-Chefe, CEO (Lexity), CIO (EESEK), CTO (ZAI)
Status: DIRETIVA FINAL APROVADA - EXECUÇÃO IMEDIATA E EXCLUSIVA

Este documento é a diretiva final e autoritária para o Agente de Implementação (AIC).
Ele incorpora a análise estratégica final do CEO (Lexity) e define o único e exclusivo
foco do projeto: a validação científica da existência de um edge.
Nenhuma outra tarefa será aceita até que esta diretiva seja executada até sua conclusão.
"""

# =====================================================
# SEÇÃO 1: DIRETIVA ESTRATÉGICA FINAL DO CEO (LEXITY)
# =====================================================

CEO_FINAL_DIRECTIVE = """
DIRETIVA EXECUTIVA FINAL: PIVÔ CIENTÍFICO E VALIDAÇÃO DE EDGE

DECISÃO: PAUSA ESTRATÉGICA TOTAL EM QUALQUER OUTRA ATIVIDADE.
REALOCAÇÃO DE 100% DOS RECURSOS PARA A VALIDAÇÃO CIENTÍFICA.

JUSTIFICATIVA:
A análise executiva confirma que o projeto estava em rota de colisão estratégica.
Estávamos investindo em infraestrutura de produção (Fase 2) para um sistema
cuja premissa fundamental (a existência de um edge explorável) nunca foi
validada. Isso é o análogo a construir uma usina de energia para uma fonte
de energia que pode não existir.

O BRILHO TÉCNICO DA IMPLEMENTAÇÃO DA FASE 2 NÃO É UM INDICADOR DE VIABILIDADE ECONÔMICA.

A única pergunta que importa agora é: "Existe ou não existe um edge?".
A única forma de responder a isso é através da ciência.

OBJETIVO IMEDIATO E ÚNICO:
Descobrir, com um nível de confiança de 95%, se pelo menos uma das hipóteses
de trading simples possui um Expected Value (E[P]) estatisticamente maior que
zero após a incorporação de todos os custos realistas de transação.

CRITÉRIO DE SUCESSO (GO/NO-GO):
- GO: Pelo menos uma hipótese com E[P] > 0, Sharpe Ratio > 0.5, e p-value < 0.05
     em um teste walk-forward.
- NO-GO: Nenhuma hipótese atende aos critérios acima.

SE NO-GO, O PROJETO SERÁ PIVOTADO OU ABANDONADO. NÃO HÁ TERCEIRO CAMINHO.

ESTA DIRETIVA NÃO É UMA SUGESTÃO. É UMA ORDEM.
"""

# =====================================================
# SEÇÃO 2: FRAMEWORK DE VALIDAÇÃO CIENTÍFICA
# =====================================================

import logging
import sys
from pathlib import Path

# Adicionar path para MetaTrader5
try:
    import MetaTrader5 as mt5
except ImportError:
    print("ERRO CRÍTICO: MetaTrader5 não instalado. Execute: pip install MetaTrader5")
    sys.exit(1)

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger("ScientificPivot")

@dataclass(frozen=True)
class ScientificConfigV3:
    """Configuração para a validação científica."""
    # --- Parâmetros de Dados ---
    SYMBOL: str = "XAUUSD"  # Gold (mais líquido que BTCUSDT no MT5)
    TIMEFRAME: int = mt5.TIMEFRAME_H1
    YEARS_OF_DATA: int = 3

    # --- Parâmetros de Custos Realistas ---
    SPREAD_BPS: float = 10.0  # 0.1%
    COMMISSION_PER_TRADE_USD: float = 5.0
    SLIPPAGE_BPS: float = 5.0  # 0.05%

    # --- Parâmetros Estatísticos ---
    SIGNIFICANCE_LEVEL: float = 0.05
    MIN_TRADES_FOR_TEST: int = 100

    # --- Parâmetros Walk-Forward ---
    WALK_FORWARD_PERIODS: int = 6  # 6 períodos de 6 meses cada
    IN_SAMPLE_RATIO: float = 0.6  # 60% in-sample, 40% out-of-sample

    # --- Hipóteses a Serem Testadas ---
    HYPOTHESES: List[str] = field(default_factory=lambda: [
        "mean_reversion_overnight_gap",
        "rsi_oversold_bounce",
        "volume_spike_continuation",
        "volatility_mean_reversion",
        "price_momentum_3d"
    ])

class HypothesisTest:
    """Classe para testar uma única hipótese de trading com dados reais."""
    def __init__(self, config: ScientificConfigV3):
        self.config = config
        self.data = self._fetch_real_data()

    def _fetch_real_data(self) -> pd.DataFrame:
        """
        OBTÉM DADOS HISTÓRICOS REAIS DO METATRADER 5.
        ESTE MÉTODO DEVE SER USADO. NÃO USE DADOS SIMULADOS.
        """
        logger.info(f"Fetching REAL data for {self.config.SYMBOL}...")
        if not mt5.initialize():
            error = mt5.last_error()
            logger.critical(f"Failed to initialize MT5: {error}")
            raise ConnectionError(f"MT5 initialization failed: {error}")
        
        try:
            utc_from = datetime.now() - timedelta(days=self.config.YEARS_OF_DATA * 365)
            utc_to = datetime.now()
            
            rates = mt5.copy_rates_range(self.config.SYMBOL, self.config.TIMEFRAME, utc_from, utc_to)
            
            if rates is None or len(rates) == 0:
                error = mt5.last_error()
                logger.critical(f"Failed to fetch data: {error}")
                raise ValueError(f"Failed to fetch data: {error}")
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Calcular indicadores técnicos básicos
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=20).std()
            df['volume_ma'] = df['tick_volume'].rolling(window=20).mean()
            
            logger.info(f"Successfully fetched {len(df)} data points from {df.index[0]} to {df.index[-1]}.")
            return df
            
        finally:
            mt5.shutdown()

    def _generate_signals(self, hypothesis_name: str) -> pd.DataFrame:
        """
        Gera sinais para uma hipótese específica.
        IMPLEMENTADO PARA TODAS AS HIPÓTESES.
        """
        signals = []
        
        if hypothesis_name == "rsi_oversold_bounce":
            # RSI Oversold Bounce: Comprar quando RSI < 30, vender quando RSI > 70
            delta = self.data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)  # Evitar divisão por zero
            rsi = 100 - (100 / (1 + rs))
            
            for i in range(14, len(self.data)):
                if rsi.iloc[i] < 30:
                    signals.append({
                        'timestamp': self.data.index[i],
                        'signal': 1,  # BUY
                        'entry_price': self.data['close'].iloc[i],
                        'entry_index': i
                    })
                elif rsi.iloc[i] > 70:
                    signals.append({
                        'timestamp': self.data.index[i],
                        'signal': -1,  # SELL
                        'entry_price': self.data['close'].iloc[i],
                        'entry_index': i
                    })
        
        elif hypothesis_name == "mean_reversion_overnight_gap":
            # Mean Reversion Overnight Gap: Reverter gaps grandes entre fechamento e abertura
            # Assumindo que cada vela H1 é um "dia" para simplificação
            df = self.data.copy()
            df['prev_close'] = df['close'].shift(1)
            df['gap'] = (df['open'] - df['prev_close']) / df['prev_close']
            df['gap_ma'] = df['gap'].rolling(window=20).mean()
            df['gap_std'] = df['gap'].rolling(window=20).std()
            
            for i in range(20, len(df)):
                gap = df['gap'].iloc[i]
                gap_zscore = (gap - df['gap_ma'].iloc[i]) / (df['gap_std'].iloc[i] + 1e-10)
                
                # Gap positivo grande = vender (reverter para baixo)
                if gap_zscore > 1.5:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': -1,  # SELL
                        'entry_price': df['open'].iloc[i],
                        'entry_index': i
                    })
                # Gap negativo grande = comprar (reverter para cima)
                elif gap_zscore < -1.5:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': 1,  # BUY
                        'entry_price': df['open'].iloc[i],
                        'entry_index': i
                    })
        
        elif hypothesis_name == "volume_spike_continuation":
            # Volume Spike Continuation: Continuar direção quando volume aumenta significativamente
            df = self.data.copy()
            df['volume_ratio'] = df['tick_volume'] / (df['volume_ma'] + 1e-10)
            df['price_change'] = df['close'].diff()
            
            for i in range(20, len(df)):
                if df['volume_ratio'].iloc[i] > 2.0:  # Volume 2x acima da média
                    price_change = df['price_change'].iloc[i]
                    # Continuar direção: comprar se subindo, vender se descendo
                    if price_change > 0:
                        signals.append({
                            'timestamp': df.index[i],
                            'signal': 1,  # BUY
                            'entry_price': df['close'].iloc[i],
                            'entry_index': i
                        })
                    elif price_change < 0:
                        signals.append({
                            'timestamp': df.index[i],
                            'signal': -1,  # SELL
                            'entry_price': df['close'].iloc[i],
                            'entry_index': i
                        })
        
        elif hypothesis_name == "volatility_mean_reversion":
            # Volatility Mean Reversion: Reverter quando volatilidade está extremamente alta ou baixa
            df = self.data.copy()
            df['volatility_ma'] = df['volatility'].rolling(window=50).mean()
            df['volatility_std'] = df['volatility'].rolling(window=50).std()
            
            for i in range(50, len(df)):
                vol = df['volatility'].iloc[i]
                vol_zscore = (vol - df['volatility_ma'].iloc[i]) / (df['volatility_std'].iloc[i] + 1e-10)
                
                # Volatilidade muito alta = esperar reversão (vender)
                if vol_zscore > 2.0:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': -1,  # SELL
                        'entry_price': df['close'].iloc[i],
                        'entry_index': i
                    })
                # Volatilidade muito baixa = esperar movimento (comprar)
                elif vol_zscore < -1.5:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': 1,  # BUY
                        'entry_price': df['close'].iloc[i],
                        'entry_index': i
                    })
        
        elif hypothesis_name == "price_momentum_3d":
            # Price Momentum 3D: Seguir momentum de 3 períodos (3 horas em H1)
            df = self.data.copy()
            df['momentum_3'] = df['close'].pct_change(periods=3)
            df['momentum_3_ma'] = df['momentum_3'].rolling(window=20).mean()
            
            for i in range(23, len(df)):  # 3 períodos + 20 para média
                momentum = df['momentum_3'].iloc[i]
                momentum_ma = df['momentum_3_ma'].iloc[i]
                
                # Momentum positivo forte = comprar
                if momentum > momentum_ma * 1.5 and momentum > 0.001:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': 1,  # BUY
                        'entry_price': df['close'].iloc[i],
                        'entry_index': i
                    })
                # Momentum negativo forte = vender
                elif momentum < momentum_ma * 1.5 and momentum < -0.001:
                    signals.append({
                        'timestamp': df.index[i],
                        'signal': -1,  # SELL
                        'entry_price': df['close'].iloc[i],
                        'entry_index': i
                    })
        
        if not signals:
            return pd.DataFrame()
        
        signals_df = pd.DataFrame(signals)
        signals_df.set_index('timestamp', inplace=True)
        return signals_df

    def _calculate_returns(self, signals: pd.DataFrame) -> pd.Series:
        """Calcula os retornos dos sinais, aplicando custos realistas."""
        if signals.empty:
            return pd.Series(dtype=float)
        
        returns = []
        
        for timestamp, signal in signals.iterrows():
            entry_index = int(signal['entry_index'])
            entry_price = signal['entry_price']
            
            # Saída na próxima vela (hold por 1 período)
            if entry_index + 1 >= len(self.data):
                continue
            
            exit_price = self.data['close'].iloc[entry_index + 1]
            
            if pd.isna(exit_price) or pd.isna(entry_price):
                continue

            # Calcular P&L baseado na direção do sinal
            if signal['signal'] == 1:  # Long
                pnl_pct = (exit_price - entry_price) / entry_price
            elif signal['signal'] == -1:  # Short
                pnl_pct = (entry_price - exit_price) / entry_price
            else:
                continue
            
            # Aplicar custos (em percentual)
            spread_cost_pct = self.config.SPREAD_BPS / 10000
            slippage_cost_pct = self.config.SLIPPAGE_BPS / 10000
            commission_cost_pct = self.config.COMMISSION_PER_TRADE_USD / (entry_price * 100)  # Assumindo 1 lote = 100 unidades
            
            total_cost_pct = spread_cost_pct + slippage_cost_pct + commission_cost_pct
            
            # Retorno líquido
            net_return = pnl_pct - total_cost_pct
            returns.append(net_return)
        
        return pd.Series(returns)

    def test_hypothesis(self, hypothesis_name: str) -> Dict[str, Any]:
        """Executa o teste estatístico completo para uma hipótese."""
        logger.info(f"Testing hypothesis: {hypothesis_name}")
        signals = self._generate_signals(hypothesis_name)

        if len(signals) < self.config.MIN_TRADES_FOR_TEST:
            return {
                "hypothesis": hypothesis_name,
                "status": "FAILED",
                "reason": f"Insufficient trades ({len(signals)} < {self.config.MIN_TRADES_FOR_TEST})",
                "total_trades": len(signals),
                "expected_value": 0.0,
                "sharpe_ratio": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "has_positive_ev": False,
                "has_acceptable_sharpe": False
            }

        returns = self._calculate_returns(signals)
        
        if len(returns) == 0 or returns.std() == 0:
            return {
                "hypothesis": hypothesis_name,
                "status": "FAILED",
                "reason": "No valid returns or zero variance",
                "total_trades": len(signals),
                "expected_value": 0.0,
                "sharpe_ratio": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "has_positive_ev": False,
                "has_acceptable_sharpe": False
            }
        
        # Teste T para E[P] > 0
        t_stat, p_value = stats.ttest_1samp(returns, 0, alternative='greater')
        
        total_trades = len(returns)
        win_rate = (returns > 0).sum() / total_trades if total_trades > 0 else 0
        expected_value = returns.mean()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252 * 24) if returns.std() > 0 else 0  # Anualizado para H1
        
        # Critérios de sucesso
        is_significant = p_value < self.config.SIGNIFICANCE_LEVEL
        has_positive_ev = expected_value > 0
        has_acceptable_sharpe = sharpe_ratio > 0.5
        
        success = is_significant and has_positive_ev and has_acceptable_sharpe

        return {
            "hypothesis": hypothesis_name,
            "status": "SUCCESS" if success else "FAILED",
            "total_trades": total_trades,
            "win_rate": win_rate,
            "expected_value": expected_value,
            "sharpe_ratio": sharpe_ratio,
            "p_value": p_value,
            "is_significant": is_significant,
            "has_positive_ev": has_positive_ev,
            "has_acceptable_sharpe": has_acceptable_sharpe,
            "returns_std": returns.std(),
            "returns_min": returns.min(),
            "returns_max": returns.max()
        }

class WalkForwardAnalyzer:
    """Análise Walk-Forward, o padrão-ouro de robustez."""
    def __init__(self, config: ScientificConfigV3, data: pd.DataFrame):
        self.config = config
        self.data = data

    def run(self, hypothesis_tester: HypothesisTest, hypothesis_name: str) -> Dict[str, Any]:
        """
        Executa a análise walk-forward.
        Esta é a validação mais importante.
        """
        logger.info(f"Running Walk-Forward Analysis for {hypothesis_name}...")
        
        total_periods = self.config.WALK_FORWARD_PERIODS
        in_sample_ratio = self.config.IN_SAMPLE_RATIO
        
        # Dividir dados em períodos
        total_length = len(self.data)
        period_length = total_length // total_periods
        
        all_out_of_sample_returns = []
        wf_results = []
        
        for period in range(total_periods):
            # Definir janelas in-sample e out-of-sample
            period_start = period * period_length
            period_end = (period + 1) * period_length
            
            if period_end > total_length:
                period_end = total_length
            
            in_sample_end = period_start + int((period_end - period_start) * in_sample_ratio)
            
            if in_sample_end >= period_end:
                continue
            
            in_sample_data = self.data.iloc[period_start:in_sample_end]
            out_of_sample_data = self.data.iloc[in_sample_end:period_end]
            
            if len(in_sample_data) < 100 or len(out_of_sample_data) < 50:
                logger.warning(f"Period {period+1}: Insufficient data. Skipping.")
                continue
            
            # Criar tester temporário com dados in-sample para otimização
            # (Por simplicidade, usamos os mesmos parâmetros, mas em produção otimizaríamos)
            temp_tester = HypothesisTest(self.config)
            temp_tester.data = in_sample_data
            
            # Gerar sinais no out-of-sample usando lógica treinada no in-sample
            signals = temp_tester._generate_signals(hypothesis_name)
            
            if signals.empty:
                continue
            
            # Filtrar sinais que estão no período out-of-sample
            out_of_sample_signals = signals[signals.index >= out_of_sample_data.index[0]]
            out_of_sample_signals = out_of_sample_signals[out_of_sample_signals.index < out_of_sample_data.index[-1]]
            
            if len(out_of_sample_signals) == 0:
                continue
            
            # Calcular retornos out-of-sample
            temp_tester.data = out_of_sample_data
            returns = temp_tester._calculate_returns(out_of_sample_signals)
            
            if len(returns) > 0:
                all_out_of_sample_returns.extend(returns.tolist())
                wf_results.append({
                    'period': period + 1,
                    'trades': len(returns),
                    'mean_return': returns.mean(),
                    'sharpe': returns.mean() / returns.std() * np.sqrt(252 * 24) if returns.std() > 0 else 0
                })
        
        if len(all_out_of_sample_returns) < self.config.MIN_TRADES_FOR_TEST:
            return {
                "status": "FAILED",
                "reason": f"Insufficient out-of-sample trades ({len(all_out_of_sample_returns)} < {self.config.MIN_TRADES_FOR_TEST})",
                "total_trades": len(all_out_of_sample_returns)
            }
        
        # Agregar resultados walk-forward
        returns_series = pd.Series(all_out_of_sample_returns)
        
        # Teste estatístico no conjunto walk-forward completo
        t_stat, p_value = stats.ttest_1samp(returns_series, 0, alternative='greater')
        
        total_trades = len(returns_series)
        win_rate = (returns_series > 0).sum() / total_trades if total_trades > 0 else 0
        expected_value = returns_series.mean()
        sharpe_ratio = returns_series.mean() / returns_series.std() * np.sqrt(252 * 24) if returns_series.std() > 0 else 0
        
        # Critérios de sucesso
        is_significant = p_value < self.config.SIGNIFICANCE_LEVEL
        has_positive_ev = expected_value > 0
        has_acceptable_sharpe = sharpe_ratio > 0.5
        
        success = is_significant and has_positive_ev and has_acceptable_sharpe
        
        return {
            "status": "SUCCESS" if success else "FAILED",
            "total_trades": total_trades,
            "win_rate": win_rate,
            "expected_value": expected_value,
            "sharpe_ratio": sharpe_ratio,
            "p_value": p_value,
            "is_significant": is_significant,
            "has_positive_ev": has_positive_ev,
            "has_acceptable_sharpe": has_acceptable_sharpe,
            "periods_tested": len(wf_results),
            "period_results": wf_results
        }

class ScientificValidator:
    """Orquestrador da validação científica."""
    def __init__(self, config: ScientificConfigV3):
        self.config = config
        self.results = []

    def run_validation(self) -> List[Dict[str, Any]]:
        """Executa a validação para todas as hipóteses."""
        logger.info("Starting scientific validation of hypotheses...")
        
        # Usar o mesmo conjunto de dados para todos os testes para consistência
        tester = HypothesisTest(self.config)
        wf_analyzer = WalkForwardAnalyzer(self.config, tester.data)

        for hypothesis in self.config.HYPOTHESES:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing hypothesis: {hypothesis}")
            logger.info(f"{'='*60}")
            
            # 1. Teste estatístico inicial
            result = tester.test_hypothesis(hypothesis)
            self.results.append(result)
            
            logger.info(f"Initial test result: {result['status']}")
            logger.info(f"  Trades: {result.get('total_trades', 0)}")
            logger.info(f"  E[P]: {result.get('expected_value', 0):.6f}")
            logger.info(f"  Sharpe: {result.get('sharpe_ratio', 0):.4f}")
            logger.info(f"  p-value: {result.get('p_value', 1):.6f}")
            
            # 2. Análise Walk-Forward (sempre executar, mesmo se teste inicial falhar)
            logger.info(f"Running Walk-Forward Analysis for {hypothesis}...")
            wf_result = wf_analyzer.run(tester, hypothesis)
            
            # Combinar resultados: Walk-Forward é mais importante
            if wf_result.get('status') == 'SUCCESS':
                result['status'] = 'SUCCESS'
                result['walk_forward'] = wf_result
                result['expected_value'] = wf_result.get('expected_value', 0)
                result['sharpe_ratio'] = wf_result.get('sharpe_ratio', 0)
                result['p_value'] = wf_result.get('p_value', 1)
                result['is_significant'] = wf_result.get('is_significant', False)
                result['has_positive_ev'] = wf_result.get('has_positive_ev', False)
                result['has_acceptable_sharpe'] = wf_result.get('has_acceptable_sharpe', False)
                result['total_trades'] = wf_result.get('total_trades', 0)
                result['walk_forward_periods'] = wf_result.get('periods_tested', 0)
                
                logger.info(f"Walk-Forward result: SUCCESS")
                logger.info(f"  Out-of-sample trades: {wf_result.get('total_trades', 0)}")
                logger.info(f"  Out-of-sample E[P]: {wf_result.get('expected_value', 0):.6f}")
                logger.info(f"  Out-of-sample Sharpe: {wf_result.get('sharpe_ratio', 0):.4f}")
                logger.info(f"  Out-of-sample p-value: {wf_result.get('p_value', 1):.6f}")
            else:
                result['walk_forward'] = wf_result
                result['status'] = 'FAILED'
                logger.info(f"Walk-Forward result: FAILED - {wf_result.get('reason', 'Unknown')}")

        return self.results

    def generate_final_report(self) -> str:
        """Gera o relatório final e decisório."""
        lines = [
            "SCIENTIFIC VALIDATION FINAL REPORT - PROMETHEUS",
            "=" * 80,
            "DECISION BASED ON EMPIRICAL EVIDENCE",
            "=" * 80,
            "",
            f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Symbol Tested: {self.config.SYMBOL}",
            f"Timeframe: H1",
            f"Years of Data: {self.config.YEARS_OF_DATA}",
            f"Total Hypotheses Tested: {len(self.results)}",
            "",
            "=" * 80,
            "EXECUTIVE SUMMARY",
            "=" * 80,
            ""
        ]
        
        successful_hypotheses = [r for r in self.results if r.get('status') == 'SUCCESS']
        
        if not successful_hypotheses:
            lines.append("CONCLUSION: NO HYPOTHESIS WAS VALIDATED.")
            lines.append("")
            lines.append("DECISION: PROJECT PIVOT OR ABANDONMENT IS MANDATORY.")
            lines.append("NO FURTHER INVESTMENT IN INFRASTRUCTURE IS JUSTIFIED.")
            lines.append("")
            lines.append("REASONING:")
            lines.append("- None of the tested hypotheses showed statistically significant edge.")
            lines.append("- Expected Value (E[P]) was not positive after transaction costs.")
            lines.append("- Sharpe Ratio did not exceed 0.5 threshold.")
            lines.append("- p-value did not meet 0.05 significance level.")
        else:
            lines.append(f"CONCLUSION: {len(successful_hypotheses)} HYPOTHESIS(ES) VALIDATED.")
            lines.append("")
            lines.append("DECISION: PROJECT MAY PROCEED TO INFRASTRUCTURE PHASE.")
            lines.append("FOCUS SHOULD BE ON THE FOLLOWING VALIDATED STRATEGIES:")
            lines.append("")
            for h in successful_hypotheses:
                lines.append(f"  ✓ {h['hypothesis']}")
                lines.append(f"    - Expected Value (E[P]): {h.get('expected_value', 0):.6f}")
                lines.append(f"    - Sharpe Ratio: {h.get('sharpe_ratio', 0):.4f}")
                lines.append(f"    - p-value: {h.get('p_value', 1):.6f}")
                lines.append(f"    - Total Trades: {h.get('total_trades', 0)}")
                lines.append(f"    - Walk-Forward Periods: {h.get('walk_forward_periods', 0)}")
                lines.append("")
        
        lines.append("=" * 80)
        lines.append("DETAILED RESULTS")
        lines.append("=" * 80)
        lines.append("")
        
        for r in self.results:
            lines.append(f"HYPOTHESIS: {r['hypothesis']}")
            lines.append(f"  Status: {r.get('status', 'UNKNOWN')}")
            lines.append(f"  Total Trades: {r.get('total_trades', 0)}")
            lines.append(f"  Win Rate: {r.get('win_rate', 0):.4f}")
            lines.append(f"  Expected Value (E[P]): {r.get('expected_value', 0):.6f}")
            lines.append(f"  Sharpe Ratio: {r.get('sharpe_ratio', 0):.4f}")
            lines.append(f"  p-value: {r.get('p_value', 1):.6f}")
            lines.append(f"  Is Significant (p < 0.05): {r.get('is_significant', False)}")
            lines.append(f"  Has Positive EV: {r.get('has_positive_ev', False)}")
            lines.append(f"  Has Acceptable Sharpe (>0.5): {r.get('has_acceptable_sharpe', False)}")
            
            if 'walk_forward' in r:
                wf = r['walk_forward']
                lines.append(f"  Walk-Forward Status: {wf.get('status', 'UNKNOWN')}")
                lines.append(f"  Walk-Forward Periods: {wf.get('periods_tested', 0)}")
                if wf.get('status') == 'FAILED':
                    lines.append(f"  Walk-Forward Reason: {wf.get('reason', 'Unknown')}")
            
            if 'reason' in r:
                lines.append(f"  Reason: {r['reason']}")
            
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)

# =====================================================
# SEÇÃO 3: DIRETIVA FINAL DE EXECUÇÃO PARA O AIC
# =====================================================

FINAL_AIC_DIRECTIVE = """
DIRETIVA FINAL E INEQUÍVOCA PARA O AGENTE DE IMPLEMENTAÇÃO (AIC)

1. EXECUÇÃO IMEDIATA E EXCLUSIVA:
   - Execute o script `scientific_pivot_final.py`.
   - Nenhuma outra tarefa de desenvolvimento ou infraestrutura deve ser realizada.
   - Seu único e exclusivo foco é a execução deste script e a entrega do relatório final.

2. IMPLEMENTAÇÃO CRÍTICA:
   - O método `_fetch_real_data` DEVE usar a API do MetaTrader 5 para obter dados históricos reais.
   - O método `_generate_signals` DEVE ser implementado para TODAS as hipóteses listadas em `HYPOTHESES`.
   - O método `run` da classe `WalkForwardAnalyzer` DEVE ser implementado. É a validação mais importante.

3. ENTREGÁVEL OBRIGATÓRIO:
   - O texto completo do relatório gerado por `generate_final_report`.
   - Cole o texto do relatório aqui. Não envie arquivos. Não envie resumos.
   - A decisão final (GO/NO-GO) será baseada 100% neste relatório.

4. CRITÉRIO DE SUCESSO:
   - GO: Pelo menos uma hipótese com E[P] > 0, Sharpe > 0.5, e p < 0.05 no walk-forward.
   - NO-GO: Nenhuma hipótese atende aos critérios.

QUALQUER RESPOSTA QUE NÃO SEJA O RELATÓRIO COMPLETO SERÁ CONSIDERADA UMA FALHA CRÍTICA
NA EXECUÇÃO DESTA DIRETIVA.

O CLOCK ESTÁ CORRENDO.
"""

def main():
    """Ponto de entrada principal para a execução da diretiva final."""
    print("="*80)
    print("SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0")
    print("FINAL EXECUTIVE DIRECTIVE: SCIENTIFIC PIVOT AND EDGE VALIDATION")
    print("VERSION 1.0 - FINAL AND AUTHORITATIVE")
    print("="*80)
    print(CEO_FINAL_DIRECTIVE)
    print("-"*80)
    print(FINAL_AIC_DIRECTIVE)
    print("="*80)
    print("\n")
    
    # Execução da validação científica
    config = ScientificConfigV3()
    validator = ScientificValidator(config)
    
    try:
        results = validator.run_validation()
    except Exception as e:
        logger.critical(f"CRITICAL FAILURE during validation: {e}", exc_info=True)
        print("\n" + "="*80)
        print("CRITICAL ERROR DURING VALIDATION")
        print("="*80)
        print(f"Error: {e}")
        print("="*80)
        return
    
    # Geração e impressão do relatório final
    final_report = validator.generate_final_report()
    print("\n" + final_report)
    print("="*80)

if __name__ == "__main__":
    main()

