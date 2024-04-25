import os
import uuid
import shutil
from fastapi import FastAPI, WebSocket, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
from typing import List

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "processed_files")

# Create the directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def process_and_move_file(src_file_path, dest_dir):
    # Simulate processing
    # Move or copy the file to the destination directory
    os.rename(src_file_path, os.path.join(dest_dir, os.path.basename(src_file_path)))


@app.get("/")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/files/", response_model=List[str])
async def list_files():
    # List all files in the folder
    files = [
        file
        for file in os.listdir(DOWNLOAD_DIR)
        if os.path.isfile(os.path.join(DOWNLOAD_DIR, file))
    ]
    return files


@app.get("/download/")
async def download_files():
<<<<<<< HEAD
    files = [
        file
        for file in os.listdir(DOWNLOAD_DIR)
        if os.path.isfile(os.path.join(DOWNLOAD_DIR, file))
    ]
    if not files:
        raise HTTPException(status_code=404, detail="No files found")

    first_file = files[0]
    file_path = os.path.join(DOWNLOAD_DIR, first_file)

    return FileResponse(file_path, filename=first_file)
=======
    if not os.path.exists(DOWNLOAD_DIR):
        raise HTTPException(status_code=404, detail="Directory not found")

    # Create a temporary directory to store the ZIP archive
    temp_dir = "temp_download"
    os.makedirs(temp_dir, exist_ok=True)

    # Create a ZIP archive of the entire directory
    zip_filename = os.path.join(temp_dir, "downloaded_files.zip")
    shutil.make_archive(os.path.splitext(zip_filename)[0], 'zip', DOWNLOAD_DIR)

    # Read the ZIP archive into a BytesIO object
    with open(zip_filename, "rb") as f:
        zip_data = BytesIO(f.read())

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    # Return the ZIP archive as a StreamingResponse
    return StreamingResponse(zip_data, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=downloaded_files.zip"})
>>>>>>> dfccd0eaafe25f5bdca94086b9a9cdeb88d24da7


@app.post("/upload/")
async def handle_file_upload(file: UploadFile = File(...)):
    # existing upload logic here

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    # Process and move the file to DOWNLOAD_DIR
    process_and_move_file(file_location, DOWNLOAD_DIR)

    return {
        "info": f"file '{file.filename}' saved at '{file_location}' and processed to {DOWNLOAD_DIR}"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome client: {websocket.client}")
    await websocket.send_text(
        "1. Audio Separation\n2. Finding Info\n3. Recommend New Songs"
    )

    while True:
        data = await websocket.receive_text()

        if data == "1":
            response = "You selected Audio Separation. Please upload your file."
            await websocket.send_text(response)
            try:
                # Receive the file from the client
                file_data = await websocket.receive_bytes()

                file_name = f"uploaded_file_{uuid.uuid4().hex[:8]}.wav"  # Generate a unique filename
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # Write the received file data to disk
                with open(file_path, "wb") as f:
                    f.write(file_data)

                # Send response back to client
                await websocket.send_text(f"File successfully uploaded to: {file_path}")
            except Exception as e:
                # Handle any errors that occur during file upload
                await websocket.send_text(f"Error uploading file: {e}")
            # web model will call upon chatbot-ish\uploaded_files and split the stems.
            # assuming that the path of the stored stems is chatbot-ish/processed_files.
            # now will make a web page where the user can download the files.

        elif data == "2":
            response = "You selected Finding Info."
            await websocket.send_text(response)
        elif data == "3":
            response = "You selected Recommend New Songs."
            await websocket.send_text(response)
        else:
            response = f"Unrecognized option: {data}. Please select 1, 2, or 3."
            await websocket.send_text(response)

        # Close the WebSocket connection only when done handling the request
        break

    await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)
