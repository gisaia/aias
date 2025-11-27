from fastapi import FastAPI, Request
import uvicorn
import threading

app = FastAPI()

@app.post("/success")
async def callback(request: Request):
    jsons = await request.body()
    print(f"{jsons}")

@app.post("/failure")
async def callback(request: Request):
    jsons = await request.body()
    print(f"{jsons}")

@app.post("/progress")
async def callback(request: Request):
    jsons = await request.body()
    print(f"{jsons}")

def run_server(port=8080):
    uvicorn.run(app, host="0.0.0.0", port=port)

# Start the server in a separate thread
#threading.Thread(target=run_server, daemon=True).start()
run_server()