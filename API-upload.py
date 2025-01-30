from fastapi import FastAPI, HTTPException
import os
import json

app = FastAPI()

@app.get('/')
async def upload_materials():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    json_path = os.path.join(parent_dir, "materials-data.json")

    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="materials-data.json not found")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data
