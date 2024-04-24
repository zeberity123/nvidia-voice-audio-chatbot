from fastapi import FastAPI, WebSocket, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def handle_file_upload(file: UploadFile = File(...)):
    # Process the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome client : {websocket.client}")
    await websocket.send_text("1. Audio Separation \n2. Finding Info \n3. Recommend New Songs")
    while True:
        data = await websocket.receive_text()

        if data == "1":
            response = "You selected Audio Separation. Please upload your file using the upload form."
        elif data == "2":
            response = "You selected Finding Info. Please provide more details..."
        elif data == "3":
            response = "You selected Recommend New Songs. Fetching recommendations..."
        else:
            response = f"Unrecognized option: {data}. Please select 1, 2, or 3."

        await websocket.send_text(response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000,
                log_level="debug", reload=True)
