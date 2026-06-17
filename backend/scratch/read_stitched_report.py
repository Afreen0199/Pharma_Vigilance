# Let us read the stitched_report.py file and inspect its lines
with open("/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered/code/stitched_report.py", "r") as f:
    lines = f.readlines()

print(f"Total lines in stitched_report.py: {len(lines)}")
for idx in range(min(120, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
