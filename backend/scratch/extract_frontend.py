import json

with open('/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered_frontend/metadata.json', 'r') as f:
    data = json.load(f)

print("Keys in metadata.json:")
for k in data.keys():
    print(f"- {k}: {len(data[k])} revisions")
