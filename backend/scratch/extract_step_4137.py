import json

transcript_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/.system_generated/logs/transcript.jsonl"
target_step = 4137

print(f"Extracting step {target_step} from transcript...")
with open(transcript_path, "r", errors="ignore") as f:
    for idx, line in enumerate(f):
        if idx + 1 == target_step:
            try:
                data = json.loads(line)
                content = data.get("content", "")
                print("Found step! Writing content to scratch/extracted_step_4137.txt...")
                with open("/Users/affu01/GRAD_PROJ_NEW/backend/scratch/extracted_step_4137.txt", "w") as out:
                    out.write(content)
                print("Done!")
            except Exception as e:
                print(f"Error: {e}")
            break
