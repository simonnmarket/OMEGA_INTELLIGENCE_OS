import os
import sys
from metrics import CodeMetrics
from statistics import TradingStatistics
from taxonomy import CodeTaxonomy

class ScientificAssessor:
    """
    Assessor Científico Central do OMEGA Intelligence OS.
    Calcula a pontuação Golden Points v2.0 baseada em métricas rigorosas.
    """

    def __init__(self):
        self.metrics_engine = CodeMetrics()
        self.stats_engine = TradingStatistics()
        self.taxonomy_engine = CodeTaxonomy()

    def analyze_module(self, filepath):
        """
        Realiza análise profunda de um arquivo.
        """
        if not os.path.exists(filepath):
            return {"error": "File not found"}

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()

        loc = len(code.splitlines())
        cc = self.metrics_engine.calculate_cyclomatic_complexity(code)
        halstead = self.metrics_engine.calculate_halstead_metrics(code)
        mi = self.metrics_engine.calculate_maintainability_index(halstead['volume'], cc, loc)
        
        taxonomy = self.taxonomy_engine.classify(code)
        
        # Cálculo de Golden Points v2.0 (Simplificado para 1a fase)
        # 30% Qualidade de Código (MI + Complexity)
        code_quality_score = (mi * 0.2) + (max(0, 10 - cc) * 1.0)
        
        # 40% Performance (Simulado sem dados históricos de backtest por enquanto)
        performance_score = 0 
        
        # 15% Inovação (Baseado na taxonomia e complexidade)
        innovation_score = (len(taxonomy['approaches']) * 3) + (halstead['difficulty'] / 10)
        
        # 15% Integração
        integration_score = 10 if taxonomy['type'] != "UNKNOWN" else 5

        total_score = code_quality_score + performance_score + innovation_score + integration_score
        
        return {
            "file": os.path.basename(filepath),
            "taxonomy": taxonomy,
            "metrics": {
                "loc": loc,
                "complexity": cc,
                "halstead": halstead,
                "maintainability_index": mi
            },
            "scores": {
                "code_quality": round(code_quality_score, 2),
                "performance": round(performance_score, 2),
                "innovation": round(innovation_score, 2),
                "integration": round(integration_score, 2),
                "total_golden_points": round(total_score, 1)
            }
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        assessor = ScientificAssessor()
        result = assessor.analyze_module(sys.argv[1])
        import json
        print(json.dumps(result, indent=4))
