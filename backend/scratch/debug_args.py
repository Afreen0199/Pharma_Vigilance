import json

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            if step_type == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    # Look at any args containing .jsx
                    str_args = str(args)
                    if ".jsx" in str_args:
                        print(f"Step {idx+1}: Tool {name}")
                        print(f"  Keys: {list(args.keys())}")
                        print(f"  TargetFile value: {repr(args.get('TargetFile'))}")
                        print(f"  Target value: {repr(args.get('Target'))}")
                        # Print first 50 chars of code content if present
                        for k in ["CodeContent", "ReplacementContent", "TargetContent"]:
                            if k in args:
                                val = str(args[k])
                                print(f"  {k} (len {len(val)}): {repr(val[:50])}")
                        print("-" * 40)
        except Exception as e:
            pass
