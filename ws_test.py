import asyncio
import websockets
import time

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws"
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempting to connect to {uri}...")
            async with websockets.connect(uri) as websocket:
                print("Connected to WebSocket server!")
                await websocket.send("Hello MCP_Stock_alert_Perplexity!")
                print("Sent test message")
                
                # Listen for messages for a short time
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"Received: {message}")
                except asyncio.TimeoutError:
                    print("No messages received in the last second, continuing...")
                    await asyncio.sleep(5)  # Wait 5 seconds before next attempt
                    
        except (websockets.exceptions.ConnectionRefused, OSError) as e:
            retry_count += 1
            print(f"Connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                print("Retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                print("Max retries reached. Make sure the MCP server is running.")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == "__main__":
    asyncio.run(test_ws())

