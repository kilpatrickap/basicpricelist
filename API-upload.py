from fastapi import FastAPI, HTTPException
import os
import json
import requests

app = FastAPI()

@app.get("/")
async def get_and_post_materials():
    """Fetch materials-data.json from parent directory and post it to an external API."""
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    json_path = os.path.join(parent_dir, "materials-data.json")

    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="materials-data.json not found")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Post the data to the external API
    try:
        response = requests.post("https://mm-api-rz05.onrender.com", json=data)
        response.raise_for_status()  # Raise an error for failed requests
        return {"status": "success", "api_response": response.json()}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to post data: {str(e)}")
