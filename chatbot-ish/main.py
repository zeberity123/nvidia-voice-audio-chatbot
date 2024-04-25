import os
import uuid
from fastapi import FastAPI, WebSocket, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

UPLOAD_DIR = "uploaded_files"

# Create the directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def handle_file_upload(file: UploadFile = File(...)):
    valid_extensions = ["wav", "mp3"]
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only WAV or MP3 files are allowed.")

    valid_mime_types = ["audio/wav", "audio/x-wav", "audio/mpeg"]
    if file.content_type not in valid_mime_types:
        raise HTTPException(
            status_code=400, detail="Invalid MIME type for the file.")

    #Changed path to UPLOAD_DIR. This directory can be modified when connecting to model.
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome client: {websocket.client}")
    await websocket.send_text("1. Audio Separation\n2. Finding Info\n3. Recommend New Songs")
    
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
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                # Send response back to client
                await websocket.send_text(f"File successfully uploaded to: {file_path}")
            except Exception as e:
                # Handle any errors that occur during file upload
                await websocket.send_text(f"Error uploading file: {e}")

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                log_level="debug", reload=True)
