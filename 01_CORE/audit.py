import json
import sys

with open('07_LOGS/SCIENTIFIC_BATCH_ANALYSIS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

targets = [
    'AdvancedPatternDetector', 'DarkPoolMonitor', 
    'VolumeProfile', 'Order Flow Analyzer',
    'OpenMyMind Project 007', 'Market Analysis Agent',
    'WeisWaveAnalyzer', 'Asymmetric Correlation Detector'
]

print("--- AUDITORIA: ARQUIVOS ENCONTRADOS NO CORE DE DADOS JSON ---")
found_count = 0
for item in data:
    path = item.get('path', '')
    for t in targets:
        if t.lower() in path.lower():
            file = item.get('file')
            tax_type = item.get('taxonomy', {}).get('type')
            score = item.get('scores', {}).get('total_golden_points')
            print(f"LIDO: {file} | TIPO: {tax_type} | PONTOS: {score}")
            found_count += 1
            
print(f"Total amostras encontradas: {found_count}")
