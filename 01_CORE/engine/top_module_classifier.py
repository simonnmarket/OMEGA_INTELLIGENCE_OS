import json
from collections import defaultdict

print('Loading JSON...')
with open('07_LOGS/SCIENTIFIC_BATCH_ANALYSIS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter valid modules
valid_modules = [m for m in data if m.get('scores', {}).get('total_golden_points', 0) > 10]
valid_modules.sort(key=lambda x: x['scores']['total_golden_points'], reverse=True)

categories = defaultdict(list)

for m in valid_modules:
    path = m.get('path', '').lower()
    name = m.get('file', '').lower()
    tax = m.get('taxonomy', {})
    type_ = tax.get('type', '').lower()
    
    score = m['scores']['total_golden_points']
    
    cat = 'Other'
    if any(x in name or x in path for x in ['risk', 'defense', 'compliance', 'hedge']):
        cat = 'Risk & Defense (Tier 2)'
    elif any(x in name or x in path for x in ['numeia', 'portfolio', 'fund', 'treasury']):
        cat = 'Fund Management (Tier 3)'
    elif any(x in name or x in path for x in ['scout', 'execution', 'hft', 'breakout']):
        cat = 'Execution Agents (Tier 1)'
    elif any(x in name or x in path for x in ['dall_elo', 'ai', 'neural', 'machine', 'elliott', 'quant']):
        cat = 'AI & Analytical Hub (Tier 4)'
    elif 'indicator' in type_:
        cat = 'Indicators'
    else:
        cat = 'General Strategies'
        
    categories[cat].append({
        'name': m['file'],
        'score': score
    })

print('\n--- TOP OMEGA ECOSYSTEM MODULES ---')
for cat in ['Execution Agents (Tier 1)', 'Risk & Defense (Tier 2)', 'Fund Management (Tier 3)', 'AI & Analytical Hub (Tier 4)', 'General Strategies', 'Indicators']:
    items = categories.get(cat, [])
    print(f'\n=== {cat} (Top 10) ===')
    for item in items[:10]:
        print(f' - [{item["score"]}] {item["name"]}')
