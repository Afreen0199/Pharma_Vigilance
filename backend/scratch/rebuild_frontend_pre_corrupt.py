import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
output_dir = "/Users/affu01/GRAD_PROJ_NEW/frontend/src"

target_files = {
    "LoginPage.jsx": "pages/LoginPage.jsx",
    "Dashboard.jsx": "pages/Dashboard.jsx",
    "UploadCasePage.jsx": "pages/UploadCasePage.jsx",
    "AnalysisWorkspace.jsx": "pages/AnalysisWorkspace.jsx",
    "FDAExplorer.jsx": "pages/FDAExplorer.jsx",
    "Sidebar.jsx": "components/layout/Sidebar.jsx",
    "Topbar.jsx": "components/layout/Topbar.jsx"
}

def clean_view_file_content(content):
    lines = content.split("\n")
    cleaned_lines = []
    header_ended = False
    for line in lines:
        if not header_ended:
            if "Showing lines" in line or "Total Lines:" in line or "File Path:" in line:
                continue
            if "The following code has been modified" in line:
                continue
            if line.strip() == "":
                continue
            header_ended = True
            
        match = re.match(r"^\s*\d+:\s?(.*)", line)
        if match:
            cleaned_lines.append(match.group(1))
        else:
            if "The above content" in line:
                continue
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

file_states = {filename: "" for filename in target_files}

print("Running chronological rebuild up to step 6500...")

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        step_number = idx + 1
        if step_number >= 6500:
            break
            
        try:
            data = json.loads(line)
            step_type = data.get("type")
            
            if step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    target_file = args.get("TargetFile", "")
                    
                    # Clean TargetFile quotes if any
                    if target_file:
                        target_file = target_file.strip('"').strip("'")
                        
                    for filename, rel_path in target_files.items():
                        if filename in target_file:
                            if name == "write_to_file":
                                code = args.get("CodeContent", "")
                                if code and "truncated" not in code.lower():
                                    file_states[filename] = code
                                    print(f"Step {step_number}: write_to_file initialized {filename} ({len(code)} bytes)")
                            elif name == "replace_file_content" and file_states[filename]:
                                target_content = args.get("TargetContent", "")
                                replacement = args.get("ReplacementContent", "")
                                if target_content in file_states[filename]:
                                    file_states[filename] = file_states[filename].replace(target_content, replacement, 1)
                                    print(f"Step {step_number}: replace_file_content applied on {filename}")
                            elif name == "multi_replace_file_content" and file_states[filename]:
                                chunks = args.get("ReplacementChunks", [])
                                print(f"Step {step_number}: multi_replace_file_content applied on {filename}")
                                for chunk in chunks:
                                    target_content = chunk.get("TargetContent", "")
                                    replacement = chunk.get("ReplacementContent", "")
                                    if target_content in file_states[filename]:
                                        file_states[filename] = file_states[filename].replace(target_content, replacement)
                                    
            elif step_type == "VIEW_FILE" and "content" in data:
                content = data["content"]
                for filename, rel_path in target_files.items():
                    expected_path = f"File Path: `file:///Users/affu01/GRAD_PROJ_NEW/frontend/src/{rel_path}`"
                    if expected_path in content:
                        match = re.search(r"Total Lines:\s*(\d+)", content)
                        showing = re.search(r"Showing lines (\d+) to (\d+)", content)
                        if match and showing:
                            total_lines = int(match.group(1))
                            start_l = int(showing.group(1))
                            end_l = int(showing.group(2))
                            if start_l == 1 and end_l >= total_lines:
                                cleaned = clean_view_file_content(content)
                                if cleaned and len(cleaned) > len(file_states[filename]):
                                    file_states[filename] = cleaned
                                    print(f"Step {step_number}: VIEW_FILE loaded full content of {filename} ({len(cleaned)} bytes)")
        except Exception as e:
            pass

# Write the final reconstructed contents back to the frontend directory
for filename, rel_path in target_files.items():
    dest_path = os.path.join(output_dir, rel_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    content = file_states[filename]
    if content:
        with open(dest_path, "w") as out:
            out.write(content)
        print(f"Successfully restored {dest_path} ({len(content)} bytes)")
    else:
        print(f"WARNING: Could not reconstruct content for {filename}!")
