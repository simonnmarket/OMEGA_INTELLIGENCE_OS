import json
import os
from collections import Counter

def generate_scientific_summary(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filtrar apenas arquivos que foram analisados com sucesso completo
    valid_data = [d for d in data if 'metrics' in d and 'scores' in d]
    invalid_count = len(data) - len(valid_data)
    
    total_files = len(valid_data)
    if total_files == 0:
        return {"error": "No valid data found"}

    total_loc = sum(d['metrics']['loc'] for d in valid_data)
    avg_complexity = sum(d['metrics']['complexity'] for d in valid_data) / total_files
    
    # Categorias
    approaches = []
    for d in valid_data:
        approaches.extend(d['taxonomy']['approaches'])
    approach_counts = Counter(approaches)
    
    types = Counter(d['taxonomy']['type'] for d in valid_data)
    
    # Top Golden Points
    top_golden = sorted(valid_data, key=lambda x: x['scores']['total_golden_points'], reverse=True)[:10]
    
    # Complexidade vs Inovação (Hidden Gems)
    gems = [d for d in valid_data if d['scores']['innovation'] > 5 and d['metrics']['complexity'] < 10]
    
    summary = {
        "total_files_analyzed": len(data),
        "successful_analysis": total_files,
        "failed_analysis": invalid_count,
        "total_loc": total_loc,
        "avg_complexity_mccabe": round(avg_complexity, 2),
        "market_approaches": dict(approach_counts),
        "module_types": dict(types),
        "golden_list": [
            {
                "file": d['file'],
                "score": d['scores']['total_golden_points'],
                "approaches": d['taxonomy']['approaches'],
                "mi": round(d['metrics']['maintainability_index'], 2)
            } for d in top_golden
        ],
        "hidden_gems_count": len(gems),
        "hidden_gems_sample": [d['file'] for d in gems[:10]]
    }
    
    return summary

if __name__ == "__main__":
    json_path = r'c:\Users\User\.gemini\antigravity\playground\ultraviolet-nadir\07_LOGS\SCIENTIFIC_BATCH_ANALYSIS.json'
    summary = generate_scientific_summary(json_path)
    print(json.dumps(summary, indent=4, ensure_ascii=False))
