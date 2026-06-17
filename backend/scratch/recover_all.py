import json
import re
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
recovered_dir = "/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered/code"
os.makedirs(recovered_dir, exist_ok=True)

targets = {
    "analyze.py": "app/routes/analyze.py",
    "report.py": "app/routes/report.py",
    "verification.py": "app/routes/verification.py",
    "fda_service.py": "app/services/fda_service.py",
    "rag_service.py": "app/services/rag_service.py",
    "report_service.py": "app/services/report_service.py",
    "database_service.py": "app/services/database_service.py",
    "semantic_retrieval_service.py": "app/services/chat/semantic_retrieval_service.py",
    "verification_service.py": "app/services/verification/verification_service.py",
    "evidence_service.py": "app/services/verification/evidence_service.py"
}

print("Scanning transcript logs...")
events = []

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            
            # 1. VIEW_FILE events
            if step_type == "VIEW_FILE" and "content" in data and "File Path" in data["content"]:
                content = data["content"]
                # Extract file path
                fp_match = re.search(r"File Path: `file://(.*?)[`\n]", content)
                if fp_match:
                    fp = fp_match.group(1)
                    matched_key = None
                    for k, v in targets.items():
                        if v in fp:
                            matched_key = k
                            break
                    if matched_key:
                        events.append({
                            "type": "VIEW",
                            "line_num": idx+1,
                            "key": matched_key,
                            "content": content
                        })
            
            # 2. PLANNER_RESPONSE events with tool calls
            elif step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    if name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                        args = tc.get("args", {})
                        target_file = args.get("TargetFile", "")
                        matched_key = None
                        for k, v in targets.items():
                            if v in target_file:
                                matched_key = k
                                break
                        if matched_key:
                            events.append({
                                "type": "TOOL_CALL",
                                "line_num": idx+1,
                                "key": matched_key,
                                "name": name,
                                "args": args
                            })
        except Exception:
            pass

print(f"Parsed {len(events)} relevant events.")

# Let us analyze each target file
for key, relative_path in targets.items():
    print(f"\n=================== {key} ===================")
    key_events = [e for e in events if e["key"] == key]
    print(f"Total events: {len(key_events)}")
    views = [e for e in key_events if e["type"] == "VIEW"]
    tool_calls = [e for e in key_events if e["type"] == "TOOL_CALL"]
    print(f"Views: {len(views)}, Tool calls: {len(tool_calls)}")
    
    # Print latest view sizes/ranges
    for v in views[-5:]:
        # Extract total lines and showing lines
        total_lines = 0
        tl_match = re.search(r"Total Lines:\s*(\d+)", v["content"])
        if tl_match:
            total_lines = int(tl_match.group(1))
        showing_match = re.search(r"Showing lines (\d+) to (\d+)", v["content"])
        showing = ""
        if showing_match:
            showing = f"{showing_match.group(1)}-{showing_match.group(2)}"
        is_trunc = "truncated" in v["content"].lower()
        print(f"  [Line {v['line_num']}] View: total={total_lines}, range={showing}, truncated={is_trunc}")
        
    for tc in tool_calls[-5:]:
        desc = tc["args"].get("Description", "")
        print(f"  [Line {tc['line_num']}] Tool Call: {tc['name']} - {desc[:50]}")
