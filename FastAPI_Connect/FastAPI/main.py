from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from typing import List

app = FastAPI()

# Define the folder where files are stored
FILES_FOLDER = "C:/Users/Harmony03/Desktop/NVauC/nvidia-voice-audio-chatbot/nvidia-voice-audio-chatbot/FastAPI_Connect/FastAPI/processed_files"

@app.get("/files/", response_model=List[str])
async def list_files():
    # List all files in the folder
    files = [file for file in os.listdir(FILES_FOLDER) if os.path.isfile(os.path.join(FILES_FOLDER, file))]
    return files

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = os.path.join(FILES_FOLDER, file_name)
    # Check if file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    # Return the file using FileResponse
    return FileResponse(file_path, filename=file_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)