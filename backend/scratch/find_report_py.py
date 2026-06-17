import json
import re

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"

print("Scanning for report.py events...")
with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            if step_type == "VIEW_FILE" and "content" in data:
                content = data["content"]
                if "app/routes/report.py" in content and "File Path:" in content:
                    lines = content.count("\n")
                    tl_match = re.search(r"Total Lines:\s*(\d+)", content)
                    tl = tl_match.group(1) if tl_match else "unknown"
                    showing = re.search(r"Showing lines (\d+) to (\d+)", content)
                    show_str = f"{showing.group(1)}-{showing.group(2)}" if showing else "unknown"
                    print(f"Step {idx+1}: VIEW_FILE, lines in content={lines}, Total Lines in header={tl}, Showing={show_str}")
            elif step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    tf = args.get("TargetFile", "")
                    if "report.py" in tf:
                        code_len = len(args.get("CodeContent", "")) if "CodeContent" in args else 0
                        rep_len = len(args.get("ReplacementContent", "")) if "ReplacementContent" in args else 0
                        print(f"Step {idx+1}: TOOL_CALL {name}, Target={tf}, CodeContent len={code_len}, ReplacementContent len={rep_len}")
        except Exception as e:
            pass
