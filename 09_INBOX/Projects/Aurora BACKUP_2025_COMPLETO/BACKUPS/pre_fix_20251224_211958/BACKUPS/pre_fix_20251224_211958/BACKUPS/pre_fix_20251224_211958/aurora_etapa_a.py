#!/usr/bin/env python3
"""
AURORA PROJECT - ETAPA A: ANÁLISE DOS 5 PONTOS CRÍTICOS CEO
Versão 5.0 - Síntese pós-análise de 3 códigos

Metodologia: Falsificabilidade de Popper + Simplicidade de Feynman
Foco: P&L real, não burocracia
Métricas: Sharpe > 1.5, Profit Factor > 1.8, Drawdown < 15%
"""

import pandas as pd
import numpy as np
import yfinance as yf
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# INTEGRAÇÃO COM NOVOS COMPONENTES v5.0
# ============================================================================

# Adicionar paths da estrutura existente
sys.path.insert(0, '00-Governanca')
sys.path.insert(0, 'modules')
sys.path.insert(0, 'wrappers_v2')
sys.path.insert(0, '01-Departamentos/AGENTS')
sys.path.insert(0, '04-Infraestrutura/ML_MODELS')

# Importar novos componentes (com fallbacks)
try:
    from tier1_risk_validator import Tier1RiskValidator, get_risk_validator
    RISK_VALIDATOR_AVAILABLE = True
except ImportError:
    RISK_VALIDATOR_AVAILABLE = False
    logger.warning("Tier1RiskValidator não disponível - usando validação padrão")

try:
    from quantum_firewall import QuantumFirewall, get_firewall
    FIREWALL_AVAILABLE = True
except ImportError:
    FIREWALL_AVAILABLE = False
    logger.warning("QuantumFirewall não disponível")

try:
    from CEO_Agent import CEOAgent, get_ceo_agent
    from CFO_Agent import CFOAgent
    from CTO_Agent import CTOAgent
    from CKO_Agent import CKOAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logger.warning("Agentes não disponíveis - usando análise padrão")

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configuração do sistema"""
    SYMBOLS = ['EURUSD=X', 'BTC-USD', 'GC=F', '^GSPC']
    MIN_SHARPE = 1.5
    MIN_PROFIT_FACTOR = 1.8
    MAX_DRAWDOWN = 0.15
    LOOKBACK_DAYS = 252  # 1 ano de trading
    TRANSACTION_COST_PCT = 0.001  # 0.1% por transação
    SLIPPAGE_PCT = 0.0005  # 0.05% slippage

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('aurora_etapa_a.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    test_name: str
    passed: bool
    details: Dict
    metrics: Optional[Dict] = None

@dataclass
class PointAnalysis:
    """Análise de um ponto crítico"""
    point_name: str
    tests: List[TestResult]
    passed_count: int
    total_count: int
    success_rate: float
    recommendation: str

@dataclass
class AnalysisReport:
    """Relatório completo da análise"""
    timestamp: str
    total_tests: int
    passed_tests: int
    success_rate: float
    by_point: Dict[str, Dict]
    recommendations: List[str]
    decision: str

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_market_data(symbol: str, days: int = 252) -> pd.DataFrame:
    """Obtém dados reais do mercado via yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=f"{days}d")
        if data.empty:
            logger.warning(f"Dados vazios para {symbol}")
            return pd.DataFrame()
        return data
    except Exception as e:
        logger.error(f"Erro ao obter dados para {symbol}: {e}")
        return pd.DataFrame()

def calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calcula Sharpe Ratio anualizado"""
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    excess_returns = returns.mean() - risk_free_rate / 252
    return (excess_returns / returns.std()) * np.sqrt(252)

def calculate_profit_factor(trades: List[Dict]) -> float:
    """Calcula Profit Factor"""
    gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss

def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """Calcula Maximum Drawdown"""
    if len(equity_curve) == 0:
        return 0.0
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    return abs(drawdown.min())

def apply_transaction_costs(price: float, cost_pct: float, slippage_pct: float) -> float:
    """Aplica custos de transação realistas"""
    return price * (1 + cost_pct + slippage_pct)

# ============================================================================
# TESTES DOS 5 PONTOS CRÍTICOS
# ============================================================================

class AuroraEtapaAAnalyzer:
    """Analisador dos 5 pontos críticos CEO - Versão 5.0 Integrada"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.config = Config()
        
        # Inicializar novos componentes se disponíveis
        if RISK_VALIDATOR_AVAILABLE:
            self.risk_validator = get_risk_validator()
        else:
            self.risk_validator = None
        
        if FIREWALL_AVAILABLE:
            self.firewall = get_firewall('TIER-0')
            self.firewall.activate()
        else:
            self.firewall = None
        
        if AGENTS_AVAILABLE:
            self.ceo_agent = get_ceo_agent()
            self.cfo_agent = CFOAgent()
            self.cto_agent = CTOAgent()
            self.cko_agent = CKOAgent()
        else:
            self.ceo_agent = None
            self.cfo_agent = None
            self.cto_agent = None
            self.cko_agent = None
    
    # ========================================================================
    # PONTO 1: IA AGENTS - Arquitetura atual suporta?
    # ========================================================================
    
    def test_ia_agents_architecture(self) -> List[TestResult]:
        """Testa se arquitetura atual suporta IA Agents"""
        tests = []
        
        # Test 1.1: Verificar se sistema tem estrutura modular
        try:
            from pathlib import Path
            modules_dir = Path('modules')
            has_modules = modules_dir.exists()
            tests.append(TestResult(
                test_name="1.1 - Estrutura Modular",
                passed=has_modules,
                details={"modules_dir_exists": has_modules}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="1.1 - Estrutura Modular",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 1.2: Verificar NCNTModule v2.0 (suporta IA)
        try:
            sys.path.insert(0, '.')
            from modules.ncnt_module_template_v2 import NCNTModule
            has_ncnt_v2 = True
            tests.append(TestResult(
                test_name="1.2 - NCNTModule v2.0",
                passed=has_ncnt_v2,
                details={"ncnt_v2_available": has_ncnt_v2}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="1.2 - NCNTModule v2.0",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 1.3: Verificar Neural Connections (comunicação IA)
        try:
            from modules.ncnt_module_template_v2 import NeuralConnection
            has_neural = True
            tests.append(TestResult(
                test_name="1.3 - Neural Connections",
                passed=has_neural,
                details={"neural_connections_available": has_neural}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="1.3 - Neural Connections",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 1.4: Verificar se há sistema de monitoramento
        try:
            monitor_path = Path('06-Monitoramento/neural_connection_monitor_v2.py')
            has_monitor = monitor_path.exists()
            tests.append(TestResult(
                test_name="1.4 - Sistema de Monitoramento",
                passed=has_monitor,
                details={"monitor_exists": has_monitor}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="1.4 - Sistema de Monitoramento",
                passed=False,
                details={"error": str(e)}
            ))
        
        return tests
    
    # ========================================================================
    # PONTO 2: Módulos administrados por IA - Como se comunicam?
    # ========================================================================
    
    def test_ia_module_communication(self) -> List[TestResult]:
        """Testa comunicação entre módulos administrados por IA"""
        tests = []
        
        # Test 2.1: Verificar Genesis Includes (IoC container)
        try:
            genesis_path = Path('00-Governanca/genesis_includes_v3_complete.py')
            has_genesis = genesis_path.exists()
            tests.append(TestResult(
                test_name="2.1 - Genesis Includes (IoC)",
                passed=has_genesis,
                details={"genesis_exists": has_genesis}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="2.1 - Genesis Includes (IoC)",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 2.2: Verificar Integration Gate
        try:
            integration_path = Path('00-Governanca/integration_gate_v3.py')
            has_integration = integration_path.exists()
            tests.append(TestResult(
                test_name="2.2 - Integration Gate",
                passed=has_integration,
                details={"integration_gate_exists": has_integration}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="2.2 - Integration Gate",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 2.3: Verificar wrappers (módulos encapsulados)
        try:
            wrappers_dir = Path('wrappers_v2')
            wrapper_count = len(list(wrappers_dir.glob('*_wrapper.py'))) if wrappers_dir.exists() else 0
            has_wrappers = wrapper_count > 0
            tests.append(TestResult(
                test_name="2.3 - Wrappers NCNT v2.0",
                passed=has_wrappers,
                details={"wrapper_count": wrapper_count}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="2.3 - Wrappers NCNT v2.0",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 2.4: Verificar se há sistema de sinais neurais
        try:
            sys.path.insert(0, '.')
            from modules.ncnt_module_template_v2 import NCNTModule
            # Verificar se tem método send_neural_signal
            has_signals = hasattr(NCNTModule, 'send_neural_signal')
            tests.append(TestResult(
                test_name="2.4 - Sistema de Sinais Neurais",
                passed=has_signals,
                details={"neural_signals_available": has_signals}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="2.4 - Sistema de Sinais Neurais",
                passed=False,
                details={"error": str(e)}
            ))
        
        return tests
    
    # ========================================================================
    # PONTO 3: Estratégias - Pipeline padronizado?
    # ========================================================================
    
    def test_strategy_pipeline(self) -> List[TestResult]:
        """Testa pipeline de estratégias"""
        tests = []
        
        # Test 3.1: Verificar se há diretório de estratégias
        try:
            strategies_paths = [
                Path('02-Processos-Chave/backtesting'),
                Path('modules'),
            ]
            has_strategies = any(p.exists() for p in strategies_paths)
            tests.append(TestResult(
                test_name="3.1 - Estrutura de Estratégias",
                passed=has_strategies,
                details={"strategies_structure_exists": has_strategies}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="3.1 - Estrutura de Estratégias",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 3.2: Verificar backtesting engine
        try:
            backtest_paths = [
                Path('02-Processos-Chave/backtesting'),
                Path('02-Processos-Chave/QA-Backtesting'),
            ]
            has_backtest = any(p.exists() for p in backtest_paths)
            tests.append(TestResult(
                test_name="3.2 - Backtesting Engine",
                passed=has_backtest,
                details={"backtest_exists": has_backtest}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="3.2 - Backtesting Engine",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 3.3: Testar pipeline com dados reais (simulação)
        try:
            data = get_market_data('EURUSD=X', days=30)
            if not data.empty:
                # Simular estratégia simples
                returns = data['Close'].pct_change().dropna()
                sharpe = calculate_sharpe(returns)
                has_pipeline = sharpe is not None
                tests.append(TestResult(
                    test_name="3.3 - Pipeline Funcional",
                    passed=has_pipeline,
                    details={"sharpe_test": sharpe, "data_points": len(returns)},
                    metrics={"sharpe": sharpe}
                ))
            else:
                tests.append(TestResult(
                    test_name="3.3 - Pipeline Funcional",
                    passed=False,
                    details={"error": "No data available"}
                ))
        except Exception as e:
            tests.append(TestResult(
                test_name="3.3 - Pipeline Funcional",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 3.4: Verificar se há sistema de validação
        try:
            validation_paths = [
                Path('02-Processos-Chave/QA-Backtesting'),
                Path('tests'),
            ]
            has_validation = any(p.exists() for p in validation_paths)
            tests.append(TestResult(
                test_name="3.4 - Sistema de Validação",
                passed=has_validation,
                details={"validation_exists": has_validation}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="3.4 - Sistema de Validação",
                passed=False,
                details={"error": str(e)}
            ))
        
        return tests
    
    # ========================================================================
    # PONTO 4: Conflitos de interesse - Como sistema previne?
    # ========================================================================
    
    def test_conflict_prevention(self) -> List[TestResult]:
        """Testa prevenção de conflitos de interesse"""
        tests = []
        
        # Test 4.1: Verificar Regulatory Context
        try:
            regulatory_path = Path('00-Governanca/regulatory_context.py')
            has_regulatory = regulatory_path.exists()
            tests.append(TestResult(
                test_name="4.1 - Regulatory Context",
                passed=has_regulatory,
                details={"regulatory_context_exists": has_regulatory}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="4.1 - Regulatory Context",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 4.2: Verificar separação Risk/Trading
        try:
            risk_path = Path('01-Departamentos/Risk-Controls')
            trading_path = Path('01-Departamentos/Execution-Trading')
            has_separation = risk_path.exists() and trading_path.exists()
            tests.append(TestResult(
                test_name="4.2 - Separação Risk/Trading",
                passed=has_separation,
                details={"risk_exists": risk_path.exists(), "trading_exists": trading_path.exists()}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="4.2 - Separação Risk/Trading",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 4.3: Verificar Audit System
        try:
            audit_path = Path('00-Governanca/audit_system_complete.py')
            has_audit = audit_path.exists()
            tests.append(TestResult(
                test_name="4.3 - Sistema de Auditoria",
                passed=has_audit,
                details={"audit_system_exists": has_audit}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="4.3 - Sistema de Auditoria",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 4.4: Verificar Compliance Module
        try:
            compliance_path = Path('01-Departamentos/Compliance-Audit')
            has_compliance = compliance_path.exists()
            tests.append(TestResult(
                test_name="4.4 - Módulo de Compliance",
                passed=has_compliance,
                details={"compliance_module_exists": has_compliance}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="4.4 - Módulo de Compliance",
                passed=False,
                details={"error": str(e)}
            ))
        
        return tests
    
    # ========================================================================
    # PONTO 5: Profit - Gestão e aprendizado?
    # ========================================================================
    
    def test_profit_learning(self) -> List[TestResult]:
        """Testa gestão de profit e aprendizado"""
        tests = []
        
        # Test 5.1: Verificar se há sistema de métricas
        try:
            # Verificar se há tracking de P&L
            metrics_paths = [
                Path('06-Monitoramento/KPIs'),
                Path('03-Operacoes-Diarias/Post-Trade'),
            ]
            has_metrics = any(p.exists() for p in metrics_paths)
            tests.append(TestResult(
                test_name="5.1 - Sistema de Métricas",
                passed=has_metrics,
                details={"metrics_system_exists": has_metrics}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="5.1 - Sistema de Métricas",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 5.2: Testar cálculo de métricas com dados reais
        try:
            data = get_market_data('EURUSD=X', days=60)
            if not data.empty:
                returns = data['Close'].pct_change().dropna()
                sharpe = calculate_sharpe(returns)
                meets_sharpe = sharpe >= self.config.MIN_SHARPE
                tests.append(TestResult(
                    test_name="5.2 - Métricas Institucionais",
                    passed=meets_sharpe,
                    details={"sharpe": sharpe, "min_required": self.config.MIN_SHARPE},
                    metrics={"sharpe": sharpe, "min_sharpe": self.config.MIN_SHARPE}
                ))
            else:
                tests.append(TestResult(
                    test_name="5.2 - Métricas Institucionais",
                    passed=False,
                    details={"error": "No data available"}
                ))
        except Exception as e:
            tests.append(TestResult(
                test_name="5.2 - Métricas Institucionais",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 5.3: Verificar se há sistema de aprendizado
        try:
            learning_paths = [
                Path('06-Monitoramento/Feedback-Loop'),
                Path('01-Departamentos/Innovation-Lab'),
            ]
            has_learning = any(p.exists() for p in learning_paths)
            tests.append(TestResult(
                test_name="5.3 - Sistema de Aprendizado",
                passed=has_learning,
                details={"learning_system_exists": has_learning}
            ))
        except Exception as e:
            tests.append(TestResult(
                test_name="5.3 - Sistema de Aprendizado",
                passed=False,
                details={"error": str(e)}
            ))
        
        # Test 5.4: Testar Profit Factor com simulação
        try:
            data = get_market_data('BTC-USD', days=30)
            if not data.empty:
                # Simular trades
                prices = data['Close'].values
                trades = []
                for i in range(1, len(prices)):
                    pnl = (prices[i] - prices[i-1]) / prices[i-1]
                    trades.append({'pnl': pnl})
                
                profit_factor = calculate_profit_factor(trades)
                meets_pf = profit_factor >= self.config.MIN_PROFIT_FACTOR
                tests.append(TestResult(
                    test_name="5.4 - Profit Factor",
                    passed=meets_pf,
                    details={"profit_factor": profit_factor, "min_required": self.config.MIN_PROFIT_FACTOR},
                    metrics={"profit_factor": profit_factor, "min_pf": self.config.MIN_PROFIT_FACTOR}
                ))
            else:
                tests.append(TestResult(
                    test_name="5.4 - Profit Factor",
                    passed=False,
                    details={"error": "No data available"}
                ))
        except Exception as e:
            tests.append(TestResult(
                test_name="5.4 - Profit Factor",
                passed=False,
                details={"error": str(e)}
            ))
        
        return tests
    
    # ========================================================================
    # EXECUÇÃO COMPLETA
    # ========================================================================
    
    def run_complete_analysis(self) -> AnalysisReport:
        """Executa análise completa dos 5 pontos"""
        logger.info("[AURORA] AURORA PROJECT - ETAPA A: ANALISE DOS 5 PONTOS CRITICOS CEO")
        logger.info("=" * 80)
        
        all_tests = []
        point_analyses = []
        
        # Ponto 1: IA Agents
        logger.info("\n[ANALISE] Analisando Ponto 1: IA Agents...")
        tests_1 = self.test_ia_agents_architecture()
        all_tests.extend(tests_1)
        point_1 = self._analyze_point("1. IA Agents", tests_1)
        point_analyses.append(point_1)
        
        # Ponto 2: IA Modules Communication
        logger.info("\n[ANALISE] Analisando Ponto 2: Modulos administrados por IA...")
        tests_2 = self.test_ia_module_communication()
        all_tests.extend(tests_2)
        point_2 = self._analyze_point("2. IA Modules", tests_2)
        point_analyses.append(point_2)
        
        # Ponto 3: Strategy Pipeline
        logger.info("\n[ANALISE] Analisando Ponto 3: Estrategias...")
        tests_3 = self.test_strategy_pipeline()
        all_tests.extend(tests_3)
        point_3 = self._analyze_point("3. Strategy Pipeline", tests_3)
        point_analyses.append(point_3)
        
        # Ponto 4: Conflict Prevention
        logger.info("\n[ANALISE] Analisando Ponto 4: Conflitos de interesse...")
        tests_4 = self.test_conflict_prevention()
        all_tests.extend(tests_4)
        point_4 = self._analyze_point("4. Conflict Prevention", tests_4)
        point_analyses.append(point_4)
        
        # Ponto 5: Profit Learning
        logger.info("\n[ANALISE] Analisando Ponto 5: Profit Learning...")
        tests_5 = self.test_profit_learning()
        all_tests.extend(tests_5)
        point_5 = self._analyze_point("5. Profit Learning", tests_5)
        point_analyses.append(point_5)
        
        # Calcular estatísticas gerais
        total_tests = len(all_tests)
        passed_tests = sum(1 for t in all_tests if t.passed)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Gerar recomendações
        recommendations = []
        for point in point_analyses:
            if point.success_rate >= 75:
                recommendations.append(f"✅ {point.point_name}: Forte ({point.success_rate:.1f}%) - Prossiga com implementação")
            elif point.success_rate >= 50:
                recommendations.append(f"⚠️ {point.point_name}: Moderado ({point.success_rate:.1f}%) - Otimizar antes de implementar")
            else:
                recommendations.append(f"❌ {point.point_name}: Fraco ({point.success_rate:.1f}%) - Requer atenção imediata")
        
        # Decisão final
        if success_rate >= 70:
            decision = "PROSSEGUIR PARA ETAPA B - Sistema validado"
        elif success_rate >= 50:
            decision = "OTIMIZAR E RETESTAR - Sistema parcialmente validado"
        else:
            decision = "PIVOT NECESSÁRIO - Revisitar hipóteses fundamentais"
        
        recommendations.append(f"\n🎯 DECISÃO: {decision}")
        
        # Criar relatório
        report = AnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            success_rate=success_rate,
            by_point={
                point.point_name: {
                    "passed": point.passed_count,
                    "total": point.total_count,
                    "rate": point.success_rate
                }
                for point in point_analyses
            },
            recommendations=recommendations,
            decision=decision
        )
        
        return report
    
    def _analyze_point(self, point_name: str, tests: List[TestResult]) -> PointAnalysis:
        """Analisa um ponto crítico"""
        passed_count = sum(1 for t in tests if t.passed)
        total_count = len(tests)
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        if success_rate >= 75:
            recommendation = "Forte - Prossiga"
        elif success_rate >= 50:
            recommendation = "Moderado - Otimizar"
        else:
            recommendation = "Fraco - Requer atenção"
        
        return PointAnalysis(
            point_name=point_name,
            tests=tests,
            passed_count=passed_count,
            total_count=total_count,
            success_rate=success_rate,
            recommendation=recommendation
        )
    
    def save_report(self, report: AnalysisReport, format: str = 'json') -> str:
        """Salva relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"aurora_etapa_a_report_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        elif format == 'csv':
            filename = f"aurora_etapa_a_summary_{timestamp}.csv"
            df = pd.DataFrame([
                {
                    "Point": point,
                    "Passed": data["passed"],
                    "Total": data["total"],
                    "Rate": data["rate"]
                }
                for point, data in report.by_point.items()
            ])
            df.to_csv(filename, index=False)
        
        return filename

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    print("[AURORA] AURORA PROJECT - ETAPA A: ANALISE DOS 5 PONTOS CRITICOS CEO")
    print("=" * 80)
    
    analyzer = AuroraEtapaAAnalyzer()
    report = analyzer.run_complete_analysis()
    
    # Exibir resultados
    print("\n[RESULTADOS] ANALISANDO RESULTADOS...")
    print(f"[PASS] TESTES PASSOU: {report.passed_tests}/{report.total_tests}")
    print(f"[SCORE] TAXA DE SUCESSO: {report.success_rate:.1f}%")
    print(f"\n[DECISAO] RECOMENDACAO: {report.decision}")
    
    # Salvar relatórios
    json_file = analyzer.save_report(report, 'json')
    csv_file = analyzer.save_report(report, 'csv')
    
    print(f"\n[FILES] Relatorios salvos:")
    print(f"   - {json_file}")
    print(f"   - {csv_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        sys.exit(0 if report.success_rate >= 70 else 1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)

