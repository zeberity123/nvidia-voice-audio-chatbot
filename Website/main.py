
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


app = FastAPI()

# directory of html templates is a folder for jinja2 templates
dist = Jinja2Templates(directory="dist")
templates = Jinja2Templates(directory="templates")

VOCALS = [{"name": "Voice Separation", "type": "mp3"}, {"name": "Additional Info", "type": "Text"}, {"name": "Singer Info", "type": "meta data"}]

# create api inpoint for jinja2 templates
@app.get('/')
async def name(request: Request):
    # return dist.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("mp3_upload.html", {"request": request})
#cd Website
# uvicorn main:app --reload
