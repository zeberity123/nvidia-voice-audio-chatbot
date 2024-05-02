from fastapi.responses import FileResponse
import os
import httpx
from fastapi import FastAPI, WebSocket, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from typing import List
import asyncio
import run_spleeter
import shazam_search
import get_SSIM_similarity
import zipfile
from fastapi import Path
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

app = FastAPI()

# Mount the static directory to serve CSS and JavaScript files
app.mount("/static", StaticFiles(directory="static"), name="static")


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FILE_DIR = os.path.join(BASE_DIR, "uploaded_files")
# DOWN_DIR = os.path.join(BASE_DIR, "processed_files")
BASE_DIR = Path(__file__).resolve().parent
FILE_DIR = BASE_DIR / "uploaded_files"
DOWN_DIR = BASE_DIR / "processed_files"

# Create the templates environment
templates_env = Environment(loader=FileSystemLoader("templates"))

os.makedirs(FILE_DIR, exist_ok=True)

AUDIO_FILENAME = ""

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Read the index.html template
    template = templates_env.get_template("index.html")

    # Render the template with the background URL
    content = template.render(request=request)

    # Return the rendered HTML content
    return HTMLResponse(content=content)


@app.get("/files/", response_model=List[str])
async def list_files():
    return [
        f for f in os.listdir(FILE_DIR) if os.path.isfile(os.path.join(FILE_DIR, f))
    ]


@app.get("/download/")
async def download_files():
    # List all files in the DOWN_DIR directory
    files_list = [
        f for f in os.listdir(DOWN_DIR) if os.path.isfile(os.path.join(DOWN_DIR, f))
    ]
    if not files_list:
        raise HTTPException(status_code=404, detail="No files found")
    print(files_list)
    return files_list


@app.get("/download/all")
async def download_all_files():
    des_name = "all_processed_files.zip"
    zip_path = os.path.join(DOWN_DIR, des_name)

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in os.listdir(DOWN_DIR):
            file_path = os.path.join(DOWN_DIR, f)
            # Ensure the current file is not the zip file being created
            if os.path.isfile(file_path) and f != des_name:
                zipf.write(file_path, arcname=f)

    run_spleeter.delete_processed()

    return FileResponse(
        path=zip_path, filename=des_name, media_type="application/octet-stream"
    )


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DOWN_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(
            path=file_path, filename=filename, media_type="application/octet-stream"
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.post("/upload/")  # index.html: function uploadFile()
async def handle_file_upload(file: UploadFile = File(...)):
    # Read the content of the uploaded file
    # Verify the file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["wav", "mp3"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Save the file to the FILE_DIR directory
    file_location = os.path.join(FILE_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    AUDIO_FILENAME = file.filename
    # background_url = shazam_search.bgr_image(f'{file_location}/{file.filename}')

    return {"info": f"File '{AUDIO_FILENAME}' saved at '{file_location}'"}


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
    await websocket.send_text("Welcome to the oooo service!")
    await asyncio.sleep(1.5)

    title = "found 0"
    artist = "found 0"
    background_image_url = ""

    reload = True
    change_file = True

    while reload:
        if change_file:
            await websocket.send_text(
                "Please upload your file. (mp3, wav format supported only)"
            )
            # as soon as the file is uploaded it should be sent to shazam_search.py to get the title, artist and background image
            filename_data = await websocket.receive_text()

            if filename_data.startswith("uploaded:"):
                filename = filename_data.split("uploaded:")[1]
                AUDIO_FILENAME = filename
                await websocket.send_text(f"uploading: {AUDIO_FILENAME}...")
                await asyncio.sleep(1.5)
                # Call the function to extract information using Shazam
                info = shazam_search.bgr_image(AUDIO_FILENAME)
                if info != 0:
                    title = info[0]
                    artist = info[1]
                    background_image_url = info[2]

            else:
                await websocket.send_text("No file uploaded.")
                await asyncio.sleep(1.5)

        await websocket.send_text(
            "Choose an option:\n"
            "1. Audio Separation\n"
            "2. Finding Info\n"
            "3. Recommend New Songs"
        )
        await asyncio.sleep(2)

        data = await websocket.receive_text()

        if data == "1":
            await websocket.send_text("You selected Audio Separation.")
            await asyncio.sleep(1)
            await websocket.send_text("Wait for Separation...")
            spl = run_spleeter.run_spleeter(AUDIO_FILENAME)

            if spl == 1:
                await websocket.send_text("An Error occurred during separation.")
                await asyncio.sleep(1.5)
            else:
                await websocket.send_text(
                    "Separation Complete. Download will start soon."
                )
                await asyncio.sleep(1.5)
                await websocket.send_text("Downloading files.")

        elif data == "2":
            # Send the extracted information back to the client

            await websocket.send_text(f"Title: {title}")
            await asyncio.sleep(0.7)
            await websocket.send_text(f"Artist: {artist}")
            await asyncio.sleep(0.7)
            await websocket.send_text("Would you like to use VocaDB? (y/n)")
            await asyncio.sleep(1)
            await websocket.send_text(f"Background Image URL: {background_image_url}")

            using_vocadb = await websocket.receive_text()

            if using_vocadb == "yes" or using_vocadb == "y":
                if title == "found 0":
                    await websocket.send_text(f"Type song title: ")
                    await asyncio.sleep(0.7)
                    title = await websocket.receive_text()

                try:
                    title = shazam_search.clean_song_title(title)
                    search_results = await search_song_vocadb(title)
                    if not search_results:
                        await websocket.send_text("No matching songs found.")
                        title = "found 0"
                    else:
                        result_messages = "\n".join(
                            [
                                f"{song['name']} by {', '.join(artist['name'] for artist in song['artists'])}"
                                for song in search_results
                            ]
                        )
                        await websocket.send_text(f"VocaDB info:\n{result_messages}")
                except httpx.ConnectError as e:
                    await websocket.send_text(
                        f"Could not connect to VocaDB API: {str(e)}"
                    )
                except Exception as e:
                    await websocket.send_text(f"Error during search: {str(e)}")

        elif data == "3":
            await websocket.send_text("Please wait...")
            path = f"uploaded_files/{AUDIO_FILENAME}"
            similarity_list = get_SSIM_similarity.get_ssim_similarity(path)
            similarity_songs = get_SSIM_similarity.get_top_n_songs(similarity_list)
            await websocket.send_text(
                f"1. {similarity_songs[0]}\n"
                f"2. {similarity_songs[1]}\n"
                f"3. {similarity_songs[2]}\n"
                f"4. {similarity_songs[3]}\n"
                f"5. {similarity_songs[4]}\n"
            )

        else:
            await websocket.send_text(
                f"Unrecognized option: {data}. Please select 1, 2, or 3."
            )
            continue

        # Ask if they want to continue with another service
        await websocket.send_text("Do you want to continue with another service? (y/n)")
        continue_operation = await websocket.receive_text()
        if continue_operation.lower() != "yes" or continue_operation.lower() != "y":
            await websocket.send_text("Thank you for using our service. Goodbye!")
            reload = False
            await websocket.close()
            break

        elif continue_operation.lower() == "yes" or continue_operation.lower() == "y":
            await websocket.send_text("Continue with same file? (y/n)")
            same_operation = await websocket.receive_text()
            if same_operation.lower() == "no" or same_operation.lower() == "n":
                reload = True
                change_file = True
                run_spleeter.delete_uploaded(AUDIO_FILENAME)
                AUDIO_FILENAME = ""
                continue  # Go back to upload file

            elif same_operation.lower() == "yes" or same_operation.lower() == "y":
                reload = True
                change_file = False
                continue  # Go back to choose option


async def search_song_vocadb(query: str) -> List[dict]:
    print(query)
    url = "https://vocadb.net/api/songs/"
    params = {"query": query, "fields": "Artists", "lang": "English"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()["items"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", workers=4, port=3939, log_level="debug", reload=True
    )
