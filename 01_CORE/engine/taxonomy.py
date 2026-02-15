import re

class CodeTaxonomy:
    """
    Engine de classificação taxonômica para códigos de trading.
    """

    KEYWORDS = {
        "SMART_MONEY": [r'liquidity', r'absorption', r'big.?player', r'institutional', r'stop.?hunt', r'imbalance'],
        "VOLUME_BASED": [r'volume.?profile', r'market.?profile', r'vwap', r'footprint', r'delta', r'poc'],
        "TECHNICAL": [r'ema', r'rsi', r'macd', r'atr', r'bollinger', r'support', r'resistance', r'trend'],
        "QUANTITATIVE": [r'machine.?learning', r'neural', r'statistical', r'optimization', r'backtest', r'probability']
    }

    TYPE_KEYWORDS = {
        "INDICATOR": [r'#property indicator', r'OnCalculate', r'iIndicator'],
        "STRATEGY": [r'Expert', r'EA', r'OnTick', r'OrderSend', r'PositionOpen'],
        "UTILITY": [r'library', r'include', r'utils', r'.mqh']
    }

    @classmethod
    def classify(cls, code):
        """
        Classifica o código baseado em padrões de palavras-chave.
        """
        results = {
            "approaches": [],
            "type": "UNKNOWN",
            "confidence": 0.0
        }

        # Identificar abordagens
        total_hits = 0
        for approach, patterns in cls.KEYWORDS.items():
            hits = 0
            for pattern in patterns:
                hits += len(re.findall(pattern, code, re.IGNORECASE))
            if hits > 0:
                results["approaches"].append(approach)
                total_hits += hits

        # Identificar tipo
        for ctype, patterns in cls.TYPE_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    results["type"] = ctype
                    break
        
        return results
