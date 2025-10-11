import asyncio
import websockets

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello MCP_Stock_alert_Perplexity!")
        while True:
            print(await websocket.recv())

asyncio.run(test_ws())

