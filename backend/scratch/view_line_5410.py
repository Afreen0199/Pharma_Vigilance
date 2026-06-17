with open("/Users/affu01/GRAD_PROJ_NEW/backend/scratch/recovered/app_routes_report.py_logs.txt", "r") as f:
    for idx, line in enumerate(f):
        if idx + 1 >= 5405 and idx + 1 <= 5425:
            print(f"Line {idx+1}: {line}")
