import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
dest_dir = "/Users/affu01/GRAD_PROJ_NEW/frontend/src"

targets = {
    "LoginPage.jsx": "pages/LoginPage.jsx",
    "Dashboard.jsx": "pages/Dashboard.jsx",
    "UploadCasePage.jsx": "pages/UploadCasePage.jsx",
    "AnalysisWorkspace.jsx": "pages/AnalysisWorkspace.jsx",
    "FDAExplorer.jsx": "pages/FDAExplorer.jsx",
    "Sidebar.jsx": "components/layout/Sidebar.jsx",
    "Topbar.jsx": "components/layout/Topbar.jsx"
}

def extract_and_stitch_jsx(filename, rel_path):
    print(f"\n--- RECONSTRUCTING {filename} ---")
    line_versions = {}
    
    with open(transcript_path, "r", errors="ignore") as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                step_type = data.get("type")
                
                # Check for VIEW_FILE
                if step_type == "VIEW_FILE" and "content" in data:
                    content = data["content"]
                    # Strictly verify if the viewed file path matches the target path in the header
                    header_pattern = r"File Path: `file:///Users/affu01/GRAD_PROJ_NEW/frontend/src/" + re.escape(rel_path) + r"`"
                    if re.search(header_pattern, content):
                        lines = content.split("\n")
                        for l in lines:
                            # Format: "N: line_content" or "<line_number>: <original_line>"
                            match = re.match(r"^\s*(\d+):\s*(.*)$", l)
                            if match:
                                num = int(match.group(1))
                                text = match.group(2)
                                line_versions[num] = text
                                
                # Check for write_to_file in PLANNER_RESPONSE
                elif step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        name = tc.get("name")
                        args = tc.get("args", {})
                        if filename in args.get("TargetFile", ""):
                            if name == "write_to_file":
                                code = args.get("CodeContent", "")
                                # Only initialize if not truncated
                                if "truncated" not in code.lower() and code:
                                    lines = code.split("\n")
                                    line_versions = {i+1: l for i, l in enumerate(lines)}
                            elif name == "replace_file_content" and line_versions:
                                # Sometimes if we can apply replacements locally we do, but view_file logs
                                # after tool calls usually capture the modified states fully!
                                pass
                                
            except Exception as e:
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
            reconstructed.append(f"// MISSING LINE {i}")
            
    print(f"Resolved lines: {len(line_versions)}/{max_line}. Missing: {len(missing)}")
    if missing:
        print(f"Missing lines: {missing[:30]}...")
        
    out_path = os.path.join(dest_dir, rel_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Save stitched file
    if reconstructed:
        with open(out_path, "w") as out_f:
            out_f.write("\n".join(reconstructed) + "\n")
        print(f"Wrote reconstructed file to: {out_path} ({len(reconstructed)} lines)")
    else:
        print(f"WARNING: No content resolved for {filename}!")

# Run for all targets
for k, v in targets.items():
    extract_and_stitch_jsx(k, v)
