'''
TIER1 RISK VALIDATOR - Validação de risco institucional
LOCAL: 00-Governanca/tier1_risk_validator.py
INTEGRAÇÃO: Compatível com estrutura existente do AURORA
'''

import logging
from datetime import datetime
from decimal import Decimal, getcontext
from typing import Dict, Tuple, List

getcontext().prec = 28

class Tier1RiskValidator:
    """
    Validador de risco Tier-1 integrado com estrutura AURORA
    Implementa padrões Goldman Sachs para gestão de risco
    """
    
    # Thresholds institucionais
    INSTITUTIONAL_THRESHOLDS = {
        'SHARPE_MIN': Decimal('1.5'),
        'PROFIT_FACTOR_MIN': Decimal('1.8'),
        'MAX_DRAWDOWN': Decimal('0.15'),
        'WIN_RATE_MIN': Decimal('0.60'),
        'MAX_POSITION_SIZE': Decimal('0.10'),
        'MAX_DAILY_LOSS': Decimal('0.05'),
        'MAX_CONCENTRATION': Decimal('0.25')
    }
    
    def __init__(self):
        self.logger = logging.getLogger("TIER1_RISK_VALIDATOR")
        self.daily_pnl = Decimal('0.0')
        self.start_date = datetime.now().date()
        
        # Integração com regulatory_context se existir
        try:
            from regulatory_context import RegulatoryContext
            self.regulatory = RegulatoryContext()
            self.logger.info("[RISK] Integrado com RegulatoryContext existente")
        except ImportError:
            self.regulatory = None
            self.logger.info("[RISK] Usando validação interna")
    
    def validate_strategy_metrics(self, metrics: Dict) -> Tuple[bool, str, Dict]:
        """
        Valida métricas de estratégia com critérios institucionais
        
        Args:
            metrics: Dicionário com métricas da estratégia
            
        Returns:
            Tuple (is_valid, message, detailed_validation)
        """
        validation_details = {}
        
        try:
            # 1. Sharpe Ratio Validation
            sharpe = Decimal(str(metrics.get('sharpe_ratio', 0)))
            sharpe_valid = sharpe >= self.INSTITUTIONAL_THRESHOLDS['SHARPE_MIN']
            validation_details['sharpe'] = {
                'value': float(sharpe),
                'threshold': float(self.INSTITUTIONAL_THRESHOLDS['SHARPE_MIN']),
                'passed': sharpe_valid,
                'weight': 0.30
            }
            
            if not sharpe_valid:
                return False, f"Sharpe Ratio insuficiente: {sharpe:.2f} < {self.INSTITUTIONAL_THRESHOLDS['SHARPE_MIN']}", validation_details
            
            # 2. Profit Factor Validation
            pf = Decimal(str(metrics.get('profit_factor', 0)))
            pf_valid = pf >= self.INSTITUTIONAL_THRESHOLDS['PROFIT_FACTOR_MIN']
            validation_details['profit_factor'] = {
                'value': float(pf),
                'threshold': float(self.INSTITUTIONAL_THRESHOLDS['PROFIT_FACTOR_MIN']),
                'passed': pf_valid,
                'weight': 0.25
            }
            
            if not pf_valid:
                return False, f"Profit Factor insuficiente: {pf:.2f} < {self.INSTITUTIONAL_THRESHOLDS['PROFIT_FACTOR_MIN']}", validation_details
            
            # 3. Max Drawdown Validation
            dd = Decimal(str(abs(metrics.get('max_drawdown', 0))))
            dd_valid = dd <= self.INSTITUTIONAL_THRESHOLDS['MAX_DRAWDOWN']
            validation_details['max_drawdown'] = {
                'value': float(dd),
                'threshold': float(self.INSTITUTIONAL_THRESHOLDS['MAX_DRAWDOWN']),
                'passed': dd_valid,
                'weight': 0.25
            }
            
            if not dd_valid:
                return False, f"Drawdown excessivo: {dd:.2%} > {self.INSTITUTIONAL_THRESHOLDS['MAX_DRAWDOWN']:.0%}", validation_details
            
            # 4. Win Rate Validation
            wr = Decimal(str(metrics.get('win_rate', 0)))
            wr_valid = wr >= self.INSTITUTIONAL_THRESHOLDS['WIN_RATE_MIN']
            validation_details['win_rate'] = {
                'value': float(wr),
                'threshold': float(self.INSTITUTIONAL_THRESHOLDS['WIN_RATE_MIN']),
                'passed': wr_valid,
                'weight': 0.20
            }
            
            if not wr_valid:
                return False, f"Win Rate insuficiente: {wr:.2%} < {self.INSTITUTIONAL_THRESHOLDS['WIN_RATE_MIN']:.0%}", validation_details
            
            # 5. Calculate Composite Score
            composite_score = self._calculate_composite_score(validation_details)
            validation_details['composite_score'] = composite_score
            
            # Sucesso - todas as validações passaram
            success_message = (
                f"Estratégia validada: Sharpe={sharpe:.2f}, PF={pf:.2f}, "
                f"DD={dd:.2%}, WR={wr:.2%}, Score={composite_score['total']:.1%}"
            )
            
            return True, success_message, validation_details
            
        except Exception as e:
            self.logger.error(f"Erro na validação: {e}")
            return False, f"Erro interno na validação: {str(e)}", validation_details
    
    def _calculate_composite_score(self, validation_details: Dict) -> Dict:
        """Calcula score composto baseado em pesos"""
        total_score = 0
        max_possible = 0
        
        for key, details in validation_details.items():
            if 'passed' in details and 'weight' in details:
                if details['passed']:
                    total_score += details['weight']
                max_possible += details['weight']
        
        total_percentage = (total_score / max_possible) if max_possible > 0 else 0
        
        return {
            'total': total_percentage,
            'raw_score': total_score,
            'max_possible': max_possible,
            'grade': self._get_grade(total_percentage)
        }
    
    def _get_grade(self, score: float) -> str:
        """Converte score em classificação"""
        if score >= 0.90:
            return 'TIER-0 (EXCELLENT)'
        elif score >= 0.80:
            return 'TIER-1 (GOOD)'
        elif score >= 0.70:
            return 'TIER-2 (ACCEPTABLE)'
        elif score >= 0.60:
            return 'TIER-3 (MARGINAL)'
        else:
            return 'FAILED'
    
    def calculate_position_size(self, portfolio_value: Decimal, 
                               risk_score: Decimal, 
                               volatility: Decimal) -> Decimal:
        """
        Calcula tamanho de posição usando Kelly Criterion adaptado
        """
        # Kelly fraction: f* = (bp - q) / b
        p = risk_score
        q = Decimal('1') - p
        b = Decimal('1.8')  # Conservative estimate
        
        # Kelly fraction
        kelly_fraction = (b * p - q) / b if b > 0 else Decimal('0')
        
        # Aplicar limite conservador
        max_kelly = Decimal('0.25')
        adjusted_fraction = min(kelly_fraction * max_kelly, 
                              self.INSTITUTIONAL_THRESHOLDS['MAX_POSITION_SIZE'])
        
        # Ajustar por volatilidade
        volatility_adjustment = Decimal('1') / (Decimal('1') + volatility * Decimal('2'))
        final_fraction = adjusted_fraction * volatility_adjustment
        
        position_size = portfolio_value * final_fraction
        
        return position_size

def get_risk_validator() -> Tier1RiskValidator:
    """Factory function para obter instância do validador"""
    return Tier1RiskValidator()

