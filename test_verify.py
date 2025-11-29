import json

with open('test_nigeria.jsonl', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

print(f'Total: {len(data)} items\n')

for i, item in enumerate(data[:3]):
    print(f"{i+1}. {item['name'][:60]}...")
    print(f"   Price: {item['current_price']} {item['currency']}")
    print(f"   URL: {item['url'][:80]}...")
    print()
