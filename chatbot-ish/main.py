import os
from fastapi import FastAPI, WebSocket, Request, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from typing import List
from fastapi import Query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.join(BASE_DIR, "files")  # Single directory for upload and download

# Ensure directory exists
os.makedirs(FILE_DIR, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/files/", response_model=List[str])
async def list_files():
    # List all files in the folder
    return [
        f for f in os.listdir(FILE_DIR) if os.path.isfile(os.path.join(FILE_DIR, f))
    ]


<<<<<<< HEAD
@app.get("/download/{filename}")
async def download_file(
    filename: str, disposition: str = Query("attachment", enum=["inline", "attachment"])
):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        filename=filename,
        headers={"Content-Disposition": f"{disposition}; filename={filename}"},
    )

=======
@app.get("/download/")
async def download_files():

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
>>>>>>> 151ad08a74e77150ca2209ae205babbeb52eb926

@app.post("/upload/")
async def handle_file_upload(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["wav", "mp3"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_location = os.path.join(FILE_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    return {"info": f"File '{file.filename}' saved at '{file_location}'"}


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
