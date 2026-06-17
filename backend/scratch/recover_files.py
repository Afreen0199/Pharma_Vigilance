import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
recovered_dir = "/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered/code"
os.makedirs(recovered_dir, exist_ok=True)

targets = {
    "analyze.py": "app/routes/analyze.py",
    "report.py": "app/routes/report.py",
    "report_service.py": "app/services/report_service.py",
    "evidence_service.py": "app/services/verification/evidence_service.py"
}

def extract_and_stitch(filename, target_path):
    print(f"\n--- RECONSTRUCTING {filename} ---")
    line_versions = {}
    
    # We will read transcript.jsonl line-by-line
    with open(transcript_path, "r", errors="ignore") as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                step_type = data.get("type")
                
                # Check for VIEW_FILE
                if step_type == "VIEW_FILE" and "content" in data and target_path in data["content"]:
                    content = data["content"]
                    # Extract lines
                    for l in content.split("\n"):
                        # Format is either "N: line_content" or "<line_number>: <original_line>"
                        match = re.match(r"^\s*(\d+):\s*(.*)$", l)
                        if match:
                            num = int(match.group(1))
                            text = match.group(2)
                            line_versions[num] = text
                            
                # Check for write_to_file/replace_file_content in PLANNER_RESPONSE
                elif step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        name = tc.get("name")
                        args = tc.get("args", {})
                        if filename in args.get("TargetFile", ""):
                            # If write_to_file and not truncated
                            if name == "write_to_file":
                                code = args.get("CodeContent", "")
                                if "truncated" not in code.lower() and code:
                                    lines = code.split("\n")
                                    line_versions = {i+1: l for i, l in enumerate(lines)}
                                    
            except Exception:
                pass
                
    max_line = max(line_versions.keys()) if line_versions else 0
    print(f"Max line number found: {max_line}")
    
    reconstructed = []
    missing = []
    for i in range(1, max_line + 1):
        if i in line_versions:
            reconstructed.append(line_versions[i])
        else:
            missing.append(i)
            reconstructed.append(f"# MISSING LINE {i}")
            
    print(f"Resolved lines: {len(line_versions)}/{max_line}. Missing: {len(missing)}")
    if missing:
        print(f"Missing lines: {missing[:30]}...")
        
    out_path = os.path.join(recovered_dir, f"stitched_{filename}")
    with open(out_path, "w") as out_f:
        out_f.write("\n".join(reconstructed) + "\n")
    print(f"Wrote to {out_path}")

# Run for targets
for k, v in targets.items():
    extract_and_stitch(k, v)
