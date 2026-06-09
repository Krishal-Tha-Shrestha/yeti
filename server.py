import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.ai import chat
from src.commands.router import handle_command

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("src/static/index.html")

@app.post("/chat")
async def chat_endpoint(payload: Message):
    command_response = handle_command(payload.text)
    if command_response:
        return {"response": command_response}
    yeti_response = chat(payload.text)
    return {"response": yeti_response}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)