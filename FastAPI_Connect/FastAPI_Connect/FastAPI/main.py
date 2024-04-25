import os
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

# Define the directory where uploaded files will be stored
UPLOAD_DIR = "uploads"

# Create the directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        # Construct the file path where the uploaded file will be stored
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}", "file_path": file_path}
