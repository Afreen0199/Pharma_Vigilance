import requests
import json

url = "http://127.0.0.1:8000/report/generate"
payload = {"analysis_id": "1ac7daee-2367-4f5e-92ed-cd1e44ded218", "force": False}
try:
    response = requests.post(url, json=payload)
    with open("scratch/api_response.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    print("Success, saved to scratch/api_response.json")
except Exception as e:
    print(f"Error: {e}")
