import re
import os

class AssetQualifier:
    """
    Motor científico para qualificar a compatibilidade de um código com diferentes 
    classes de ativos (Forex, Metais, Índices, Crypto).
    """
    
    ASSET_PATTERNS = {
        "METALS": [r'XAU', r'XAG', r'GOLD', r'SILVER', r'TickValue.*0\.01'],
        "INDICES": [r'SPX', r'NAS', r'US30', r'GER40', r'Indices'],
        "JPY_PAIRS": [r'JPY', r'CarryTrade', r'Yen'],
        "GBP_PAIRS": [r'GBP', r'Cable', r'Guppy'],
        "CRYPTO": [r'BTC', r'ETH', r'Crypto', r'24/7'],
    }

    @classmethod
    def analyze_asset_bias(cls, code):
        bias = []
        for asset, patterns in cls.ASSET_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    bias.append(asset)
                    break
        
        return {
            "detected_bias": bias,
            "universal_potential": len(bias) == 0,
            "specialization_level": "SPECIALIZED" if len(bias) > 0 else "GENERALIST"
        }

    @classmethod
    def get_regime_recommendation(cls, asset_type, results=None):
        """
        Retorna a recomendação baseada no regime do ativo.
        """
        regimes = {
            "JPY_PAIRS": "Trend-Volatility (Best for breakouts)",
            "METALS": "High Persistence (Best for trend following)",
            "INDICES": "Mean Reversion w/ Bullish Bias",
            "FOREX_MAJORS": "High Liquidity (Best for Scalping)",
        }
        return regimes.get(asset_type, "Standard Regime")

if __name__ == "__main__":
    # Teste rápido
    test_code = "bool isGold = StringFind(_Symbol, 'XAU') >= 0; double tick = 0.01;"
    print(AssetQualifier.analyze_asset_bias(test_code))
