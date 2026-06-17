import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
output_dir = "/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered_frontend"
os.makedirs(output_dir, exist_ok=True)

target_files = [
    "LoginPage.jsx",
    "Dashboard.jsx",
    "UploadCasePage.jsx",
    "AnalysisWorkspace.jsx",
    "FDAExplorer.jsx",
    "Sidebar.jsx",
    "Topbar.jsx"
]

print("Scanning transcript for frontend JSX files...")

recovered_contents = {name: [] for name in target_files}

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            
            # Check for tool calls in planner responses
            if step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    target_file = args.get("TargetFile", "")
                    
                    for filename in target_files:
                        if filename in target_file:
                            print(f"Step {idx+1}: Tool {name} targeted {target_file}")
                            
                            code = args.get("CodeContent")
                            repl = args.get("ReplacementContent")
                            chunks = args.get("ReplacementChunks")
                            
                            entry = {
                                "step": idx + 1,
                                "tool": name,
                                "target": target_file,
                                "code": code,
                                "replacement": repl,
                                "chunks": chunks
                            }
                            recovered_contents[filename].append(entry)
                            
            # Check for standard view file outputs in the logs to see if we read them
            if step_type == "VIEW_FILE" and "content" in data:
                content = data["content"]
                for filename in target_files:
                    if filename in content and "File Path:" in content:
                        print(f"Step {idx+1}: VIEW_FILE contained {filename}")
                        recovered_contents[filename].append({
                            "step": idx + 1,
                            "tool": "VIEW_FILE",
                            "content": content
                        })
        except Exception as e:
            pass

# Let's save the findings to a json for inspection
with open(os.path.join(output_dir, "metadata.json"), "w") as out:
    json.dump(recovered_contents, out, indent=2, default=str)

print("Scan complete. Metadata written to scratch/recovered_frontend/metadata.json.")
