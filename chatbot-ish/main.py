import os
import uuid
import httpx
from fastapi import FastAPI, WebSocket, Request, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from typing import List

import run_spleeter

# Setup directory for file uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(FILE_DIR, exist_ok=True)  # Ensure directory exists


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/files/", response_model=List[str])
async def list_files():
    return [
        f for f in os.listdir(FILE_DIR) if os.path.isfile(os.path.join(FILE_DIR, f))
    ]


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


@app.post("/upload/")
async def handle_file_upload(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["wav", "mp3"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_location = os.path.join(FILE_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
        print(f"File '{file.filename}' saved at '{file_location}'")
    AUDIO_FILENAME = file.filename
    return {"info": f"File '{file.filename}' saved at '{file_location}'"}


# @app.post("/separation/")
# async def audio_separation(filename: str = AUDIO_FILENAME):
#     message = "separation failed"
#     try:
#         run_spleeter.run_spleeter(filename)
#         message = "done"
#     except Exception as e:
#         print(f"An error occurred: {e}")

#     return message


@app.get("/search/")
async def search_files(query: str):
    matching_files = [
        f
        for f in os.listdir(FILE_DIR)
        if query.lower() in f.lower() and os.path.isfile(os.path.join(FILE_DIR, f))
    ]
    if not matching_files:
        raise HTTPException(status_code=404, detail="No matching files found")
    return matching_files


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome to the audio service!")
    await websocket.send_text(
        "Choose an option:\n1. Audio Separation\n2. Finding Info\n3. Recommend New Songs"
    )

    while True:
        data = await websocket.receive_text()

        if data == "1":
            await websocket.send_text(
                "You selected Audio Separation. Please upload your file."
            )
            # Wait to receive the filename from the client
            filename_data = await websocket.receive_text()

            if filename_data.startswith("uploaded:"):
                filename = filename_data.split("uploaded:")[1]
                await websocket.send_text(f"You've uploaded {filename}.")
                await websocket.send_text(
                    "Wait for separation..."
                )  # Inform user to wait

                # Perform the audio separation here
                try:
                    # Assuming 'run_spleeter' is a function that takes a filename and processes it
                    await run_spleeter.run_spleeter(filename)
                    await websocket.send_text("Separation completed successfully.")
                except Exception as e:
                    await websocket.send_text(
                        f"An error occurred during separation: {str(e)}"
                    )

            else:
                await websocket.send_text("No file uploaded.")

        elif data == "2":
            # Additional logic for options 2 and 3
            pass

        continue_operation = await websocket.receive_text()
        if continue_operation.lower() != "yes":
            await websocket.send_text("Thank you for using our service. Goodbye!")
            break

    await websocket.close()


async def search_song_vocadb(query: str) -> List[dict]:
    url = "https://vocadb.net/api/songs"  # Adjust to the actual VocaDB API URL
    params = {"query": query, "fields": "Artists", "lang": "English"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()["items"]


def test_vocadb_api():
    # Example: Adjusted to hypothetical public API endpoint
    url = "https://api.vocadb.net/api/songs"
    params = {"query": "test song", "fields": "Artists", "lang": "English"}
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            print(response.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    import uvicorn

    # Optionally test the VocaDB connection when the script runs
    test_vocadb_api()  # Consider commenting this out in production
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)
