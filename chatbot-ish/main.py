from fastapi import FastAPI, WebSocket, Request

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

app = FastAPI()
# html파일을 서비스할 수 있는 jinja설정 (/templates 폴더사용)
templates = Jinja2Templates(directory="templates")


# 웹소켓 연결을 테스트 할 수 있는 웹페이지 (http://127.0.0.1:8000/client)
@app.get("/client")
async def client(request: Request):
    # /templates/client.html파일을 response함
    return templates.TemplateResponse("index.html", {"request": request})


# 웹소켓 설정 ws://127.0.0.1:8000/ws 로 접속할 수 있음
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept()  # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    while True:
        data = await websocket.receive_text()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")
        await websocket.send_text(f"Message text was: {data}")  # client에 메시지 전달


# 개발/디버깅용으로 사용할 앱 구동 함수
def run():
    import uvicorn

    uvicorn.run(app)


# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()
