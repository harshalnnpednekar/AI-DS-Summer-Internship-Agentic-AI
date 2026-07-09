import json

with open('events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('| Date | Event Name | Department |')
print('|---|---|---|')
for e in data['events']:
    print(f"| {e.get('date', '')} | {e.get('title', '')} | {e.get('department', '')} |")
