from typing import Optional, List

from fastapi import FastAPI, WebSocket, Request, Cookie, Depends, Query, status, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials= True,
    allow_methods= ["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    # บันทึก Client ที่ออนไลน์ไว้ใน list
    def __init__(self):
        self.active_connections: List[Websocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # ส่งค่าไปแสดงผลในหน้า index.html (เข้า javascript)
    async def send_personal_message(self, message: str, websocket: WebSocket):
        #await websocket.send_text(message)
        print(f"message = \"{message}\"")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


# Render index.html
@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})


#  async def get_cookie_or_token(websocket: WebSocket,
                              #  session: Optional[str] = Cookie(None),
                              #  token: Optional[str] = Query(None),):
    #  if session is None and token is None:
        #  await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #  return session or token


#  @app.websocket("/items/{item_id}/ws")
#  async def websocket_endpoint(websocket: WebSocket, item_id: str,
                             #  q: Optional[int] = None,
                             #  cookie_or_token: str = Depends(get_cookie_or_token),):
    #  await websocket.accept()
    #  while True:
        #  data = await websocket.receive_text()
        #  await websocket.send_text(f"Session cookie or query token value is: {cookie_or_token}")
        #  if q is not None:
            #  await websocket.send_text(f"Query parameter q is: {q}")
        #  await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")


# Receive client_id and text_message from index.html (javascript)
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            global data
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} say: {data}")
            #  print("data = ",data[:6])
            if "trans-" in data[:6]:
                text_msg = data[6:]     # ยังไม่ตัด space และยังเลือกภาษาไม่ได้
                await translate_message(text_msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


# Translate
@app.post("/translate={text_msg}")
async def translate_message(text_msg: str):
    print(f"from client: {text_msg}")
    try:
        from Translated import translation

        trans = translation(text_msg)
        print(u"Translated to 'de': {}".format(trans["translatedText"]))
        await manager.broadcast(u"Bot: {} to 'de' = {}.".format(text_msg, trans["translatedText"]))
        return trans
    except Exception as e:
        return str(f"Can not translate this message! ({text_msg}). An error: {e}")
