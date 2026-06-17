import json
import os

with open('/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered_frontend/metadata.json', 'r') as f:
    data = json.load(f)

output_path = '/Users/affu01/GRAD_PROJ_NEW/backend/scratch/metadata_details.txt'
with open(output_path, 'w') as out:
    for filename, revisions in data.items():
        out.write(f"\n==================== {filename} ====================\n")
        for idx, rev in enumerate(revisions):
            step = rev.get("step")
            tool = rev.get("tool")
            target = rev.get("target")
            
            content = rev.get("content") or rev.get("code") or ""
            repl = rev.get("replacement") or ""
            chunks = rev.get("chunks") or ""
            
            c_len = len(content)
            r_len = len(repl)
            ch_len = len(str(chunks))
            
            out.write(f"Revision {idx}: Step {step} | Tool: {tool} | Content Len: {c_len} | Replacement Len: {r_len} | Chunks: {ch_len}\n")
            if c_len > 0:
                out.write(f"  Content Preview: {content[:200].replace('\n', ' ')}...\n")
            if r_len > 0:
                out.write(f"  Replacement Preview: {repl[:200].replace('\n', ' ')}...\n")

print(f"Details written to {output_path}")
