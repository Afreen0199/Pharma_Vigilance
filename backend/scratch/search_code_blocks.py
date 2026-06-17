import json
import re

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"

print("Scanning transcript for markdown code blocks...")

with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step_type = data.get("type")
            
            # Check for planner text response content
            if step_type == "PLANNER_RESPONSE" and "content" in data:
                content = data["content"]
                
                # Check if there are JSX/JS code blocks
                if "```" in content:
                    # Let's search for file signatures or keywords
                    keywords = ["LoginPage", "UploadCasePage", "AnalysisWorkspace", "FDAExplorer", "Dashboard", "Sidebar", "Topbar"]
                    found = [kw for kw in keywords if kw in content]
                    if found:
                        print(f"\nStep {idx+1}: Found code block mentioning {found}")
                        # Print code block boundaries
                        blocks = re.findall(r"```(?:javascript|jsx|js)?\n(.*?)\n```", content, re.DOTALL)
                        for b_idx, block in enumerate(blocks):
                            # Print first 2 lines and last 2 lines
                            lines = block.split("\n")
                            print(f"  Block {b_idx+1}: {len(lines)} lines. Starts with: {lines[:2]} ... Ends with: {lines[-2:]}")
        except Exception as e:
            pass
