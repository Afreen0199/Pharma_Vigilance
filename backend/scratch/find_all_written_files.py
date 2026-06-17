import json
import os

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"

written_files = set()

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            if step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    if name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                        args = tc.get("args", {})
                        target_file = args.get("TargetFile", "")
                        if target_file:
                            written_files.add(target_file)
        except Exception as e:
            pass

print("All files written to in the transcript:")
for f in sorted(list(written_files)):
    print(f"- {f}")
