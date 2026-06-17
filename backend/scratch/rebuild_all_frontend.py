import json
import os
import re

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
output_dir = "/Users/affu01/GRAD_PROJ_NEW/frontend/src"

target_files = {
    "LoginPage.jsx": "pages/LoginPage.jsx",
    "Dashboard.jsx": "pages/Dashboard.jsx",
    "UploadCasePage.jsx": "pages/UploadCasePage.jsx",
    "AnalysisWorkspace.jsx": "pages/AnalysisWorkspace.jsx",
    "FDAExplorer.jsx": "pages/FDAExplorer.jsx",
    "Sidebar.jsx": "components/layout/Sidebar.jsx",
    "Topbar.jsx": "components/layout/Topbar.jsx",
    "SafetyChatbot.jsx": "components/chatbot/SafetyChatbot.jsx",
    "DynamicReportRenderer.jsx": "components/reports/DynamicReportRenderer.jsx",
    "TimelineUI.jsx": "components/timeline/TimelineUI.jsx"
}

file_states = {filename: "" for filename in target_files}

print("Running pure tool-call chronological rebuild for all 10 files...")

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            
            if step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    target_file = args.get("TargetFile", "")
                    
                    for filename, rel_path in target_files.items():
                        if filename in target_file:
                            if name == "write_to_file":
                                code = args.get("CodeContent", "")
                                if code and "truncated" not in code.lower():
                                    file_states[filename] = code
                                    print(f"Step {idx+1}: write_to_file initialized {filename} ({len(code)} bytes)")
                            elif name == "replace_file_content" and file_states[filename]:
                                target_content = args.get("TargetContent", "")
                                replacement = args.get("ReplacementContent", "")
                                if target_content in file_states[filename]:
                                    file_states[filename] = file_states[filename].replace(target_content, replacement, 1)
                                    print(f"Step {idx+1}: replace_file_content applied on {filename}")
                                else:
                                    target_stripped = target_content.strip()
                                    if target_stripped and target_stripped in file_states[filename]:
                                        file_states[filename] = file_states[filename].replace(target_stripped, replacement, 1)
                                        print(f"Step {idx+1}: replace_file_content fuzzy matched on {filename}")
                                    else:
                                        # Let's print out if it fails to find TargetContent, but wait, it might be due to line endings or spacing differences
                                        pass
                            elif name == "multi_replace_file_content" and file_states[filename]:
                                chunks = args.get("ReplacementChunks", [])
                                print(f"Step {idx+1}: multi_replace_file_content applied {len(chunks)} chunks on {filename}")
                                for chunk in chunks:
                                    target_content = chunk.get("TargetContent", "")
                                    replacement = chunk.get("ReplacementContent", "")
                                    if target_content in file_states[filename]:
                                        file_states[filename] = file_states[filename].replace(target_content, replacement)
                                    else:
                                        target_stripped = target_content.strip()
                                        if target_stripped and target_stripped in file_states[filename]:
                                            file_states[filename] = file_states[filename].replace(target_stripped, replacement)
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
