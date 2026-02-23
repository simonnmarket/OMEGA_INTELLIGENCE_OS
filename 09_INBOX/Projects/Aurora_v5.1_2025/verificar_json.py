import json

with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("AURORA MODULES SPEC.JSON")
print("=" * 60)
print(f"\nTotal módulos: {data['metadata']['total_modules']}")
print(f"Categorias: {data['metadata']['categories']}")
print(f"Gerado em: {data['metadata']['generated']}")
print("\nDistribuição por categoria:")
for k, v in sorted(data['categorized'].items()):
    print(f"  {k}: {v} módulos")
print("\n" + "=" * 60)
print(f"Arquivo: aurora_modules_spec.json")
print(f"Localização: C:\\Users\\Lenovo\\Projects\\Aurora\\aurora_modules_spec.json")
print("=" * 60)

