import re
import math

class CodeMetrics:
    """
    Engine para cálculo de métricas de qualidade de código.
    Baseado em McCabe (1976) e Halstead (1977).
    """

    @staticmethod
    def calculate_cyclomatic_complexity(code):
        """
        Calcula a Complexidade Ciclomática (CC).
        CC = decision_points + 1
        """
        decision_keywords = [
            r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bwhile\b', 
            r'\bcase\b', r'\bcatch\b', r'\band\b', r'\bor\b', r'\b&&\b', r'\b\|\|\b'
        ]
        count = 0
        for kw in decision_keywords:
            count += len(re.findall(kw, code))
        return count + 1

    @staticmethod
    def calculate_halstead_metrics(code):
        """
        Calcula as métricas de Halstead.
        """
        # Simplificação para estimativa
        operators = set(re.findall(r'[\+\-\*/%=<>&|^!~]+|\b(if|else|for|while|return|switch|case|break)\b', code))
        operands = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\d+', code)) - operators
        
        n1 = len(operators)
        n2 = len(operands)
        N1 = len(re.findall(r'[\+\-\*/%=<>&|^!~]+|\b(if|else|for|while|return|switch|case|break)\b', code))
        N2 = len(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\d+', code))
        
        vocabulary = n1 + n2
        length = N1 + N2
        
        if vocabulary > 0:
            volume = length * math.log2(vocabulary)
        else:
            volume = 0
            
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = difficulty * volume
        bugs = volume / 3000
        
        return {
            "vocabulary": vocabulary,
            "length": length,
            "volume": round(volume, 2),
            "difficulty": round(difficulty, 2),
            "effort": round(effort, 2),
            "estimated_bugs": round(bugs, 4)
        }

    @staticmethod
    def calculate_maintainability_index(volume, cc, loc):
        """
        Calcula o Índice de Manutenibilidade (MI).
        Fórmula padrão: 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
        """
        if volume <= 0 or loc <= 0:
            return 100
        
        mi = 171 - 5.2 * math.log(volume) - 0.23 * cc - 16.2 * math.log(loc)
        # Normalizar para 0-100
        mi = max(0, min(100, (mi * 100) / 171))
        return round(mi, 2)
