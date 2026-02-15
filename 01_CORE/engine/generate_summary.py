import json
import os
from collections import Counter

def generate_scientific_summary(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_files = len(data)
    total_loc = sum(d['metrics']['loc'] for d in data)
    
    # Categorias
    approaches = []
    for d in data:
        approaches.extend(d['taxonomy']['approaches'])
    approach_counts = Counter(approaches)
    
    types = Counter(d['taxonomy']['type'] for d in data)
    
    # Top Golden Points
    top_golden = sorted(data, key=lambda x: x['scores']['total_golden_points'], reverse=True)[:10]
    
    # Complexidade vs Inovação (Hidden Gems)
    # Gems: Alta inovação (>5) e baixa complexidade (<10)
    gems = [d for d in data if d['scores']['innovation'] > 5 and d['metrics']['complexity'] < 10]
    
    # Estatísticas de Qualidade
    avg_mi = sum(d['metrics']['maintainability_index'] for d in data) / total_files
    avg_cc = sum(d['metrics']['complexity'] for d in data) / total_files

    summary = {
        "total_files": total_files,
        "total_loc": total_loc,
        "avg_maintainability": round(avg_mi, 2),
        "avg_complexity": round(avg_cc, 2),
        "approach_distribution": dict(approach_counts),
        "type_distribution": dict(types),
        "top_10_golden_modules": [
            {
                "file": d['file'],
                "score": d['scores']['total_golden_points'],
                "approaches": d['taxonomy']['approaches'],
                "mi": d['metrics']['maintainability_index']
            } for d in top_golden
        ],
        "hidden_gems_count": len(gems),
        "hidden_gems_sample": [d['file'] for d in gems[:5]]
    }
    
    return summary

if __name__ == "__main__":
    json_path = r'c:\Users\User\.gemini\antigravity\playground\ultraviolet-nadir\07_LOGS\SCIENTIFIC_BATCH_ANALYSIS.json'
    summary = generate_scientific_summary(json_path)
    print(json.dumps(summary, indent=4, ensure_ascii=False))
