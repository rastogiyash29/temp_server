import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    x = 0
    try:
        async for data in websocket.iter_text():
            asyncio.create_task(manager.broadcast(f"Client Says: {data}", websocket,x))
            x = x+1
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, int] = {}
        self.request_counter = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.request_counter += 1
        self.active_connections[websocket] = self.request_counter

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket,reqNum:int):
        request_num = self.active_connections[websocket]
        await self.send_personal_message(f"Received request number: {reqNum} from client", websocket)

        num_responses = random.randint(2, 5)
        tasks = []
        for i in range(num_responses):
            response_message = f"Server response reqNum->{reqNum}<-  responseNum:{i + 1}"
            delay = random.uniform(1, 10)
            task = asyncio.create_task(self.send_response(websocket, response_message, delay))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def send_response(self, websocket: WebSocket, response_message: str, delay: float):
        await asyncio.sleep(delay)
        await self.send_personal_message(response_message, websocket)

manager = ConnectionManager()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
