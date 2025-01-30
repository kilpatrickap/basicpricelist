import os
import json
import requests

# Read the materials-data.json file
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
json_path = os.path.join(parent_dir, "materials-data.json")

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Post the data to the API root `/`
response = requests.post("https://mm-api-rz05.onrender.com", json=data)

# Check the response
if response.status_code == 200:
    print("Data uploaded successfully")
else:
    print(f"Failed to upload data: {response.status_code} - {response.text}")
