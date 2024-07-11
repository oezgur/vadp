import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:5173"
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        while True:
            try:
                message = await websocket.recv()
                print(f"Message from server: {message}")
            except websockets.ConnectionClosed:
                print("Connection closed")
                break

asyncio.run(test_connection())
