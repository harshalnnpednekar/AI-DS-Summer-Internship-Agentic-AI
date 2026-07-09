import json
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'events.json'

with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('| Date | Event Name | Department |')
print('|---|---|---|')
for e in data['events']:
    print(f"| {e.get('date', '')} | {e.get('title', '')} | {e.get('department', '')} |")
