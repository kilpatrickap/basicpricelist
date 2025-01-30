from fastapi import FastAPI, HTTPException
import os
import json
from fastapi.responses import JSONResponse

app = FastAPI()

# GET request for fetching the data
@app.get("/")
async def get_materials():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    json_path = os.path.join(parent_dir, "materials-data.json")

    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="materials-data.json not found")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


# POST request for uploading data
@app.post("/")
async def upload_materials(data: dict):
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    json_path = os.path.join(parent_dir, "materials-data.json")

    # Save the data to materials-data.json
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return JSONResponse(content={"message": "Data uploaded successfully"}, status_code=200)
