import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
recovered_dir = "/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered/code"
os.makedirs(recovered_dir, exist_ok=True)

targets = {
    "analyze.py": {
        "path_pattern": "app/routes/analyze.py",
        "final_total_lines": 383
    },
    "report.py": {
        "path_pattern": "app/routes/report.py",
        "final_total_lines": 616
    },
    "report_service.py": {
        "path_pattern": "app/services/report_service.py",
        "final_total_lines": 266
    },
    "evidence_service.py": {
        "path_pattern": "app/services/verification/evidence_service.py",
        "final_total_lines": 165
    },
    "verification_service.py": {
        "path_pattern": "app/services/verification/verification_service.py",
        "final_total_lines": 81
    }
}

def extract_for_target(name, info):
    print(f"\n--- RECONSTRUCTING {name} ---")
    line_versions = {}
    path_pat = info["path_pattern"]
    total_lines_limit = info["final_total_lines"]
    
    with open(transcript_path, "r", errors="ignore") as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                step_type = data.get("type")
                
                # Check for VIEW_FILE
                if step_type == "VIEW_FILE" and "content" in data:
                    content = data["content"]
                    if path_pat in content and "File Path:" in content:
                        # Find the Total Lines in this view
                        t_match = re.search(r"Total Lines:\s*(\d+)", content)
                        if t_match:
                            view_total = int(t_match.group(1))
                            # Only parse if this view matches or is very close to final total lines
                            # or let us parse it but map the lines correctly.
                            # Actually, let us parse all lines, but if view_total <= final_total_lines, 
                            # we can map them. If it is an older view, it might have fewer lines, 
                            # but unchanged lines are still correct.
                            lines = content.split("\n")
                            for l in lines:
                                match = re.match(r"^\s*(\d+):\s*(.*)$", l)
                                if match:
                                    num = int(match.group(1))
                                    text = match.group(2)
                                    if num <= view_total:
                                        # To avoid mapping shifted line numbers, we will only map them if
                                        # the view_total matches the target total lines or we map them dynamically.
                                        # Let us save it under a tuple: (view_total, num) -> text
                                        line_versions[(view_total, num)] = text
                                        
            except Exception:
                pass
                
    # Now, let us check which view totals we found
    view_totals = sorted(list(set(k[0] for k in line_versions.keys())))
    print(f"Found views with total lines: {view_totals}")
    
    # We will reconstruct the final file using the latest view_total (which should be final_total_lines)
    # If some lines are missing from the latest view, we can check previous views (with fallback)
    reconstructed = []
    missing = []
    
    # Target total lines to build
    target_total = total_lines_limit
    
    # Find the best view totals to fallback
    # We want to check fallback in descending order of view totals
    fallback_totals = sorted(view_totals, reverse=True)
    
    for i in range(1, target_total + 1):
        line_text = None
        for t in fallback_totals:
            # If we are looking at an older view (t < target_total), line numbers might have shifted.
            # But let us assume no shift first, or if there is a shift, we can inspect.
            # Actually, let us check if the exact line exists in (t, i)
            if (t, i) in line_versions:
                line_text = line_versions[(t, i)]
                break
        if line_text is not None:
            reconstructed.append(line_text)
        else:
            missing.append(i)
            reconstructed.append(f"# MISSING LINE {i}")
            
    print(f"Resolved lines: {target_total - len(missing)}/{target_total}. Missing: {len(missing)}")
    if missing:
        print(f"Missing lines: {missing[:30]}...")
        
    out_path = os.path.join(recovered_dir, f"clean_stitched_{name}")
    with open(out_path, "w") as out_f:
        out_f.write("\n".join(reconstructed) + "\n")
    print(f"Wrote to {out_path}")

for k, v in targets.items():
    extract_for_target(k, v)
