import os
os.environ['CUDA_VISIBLE_DEVICES'] = "1"
os.environ['NVIDIA_VISIBLE_DEVICES'] = "1"
import uvicorn
from fastapi import FastAPI, APIRouter
import argparse
from main.bot.api import router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from main.audio import program

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with the appropriate origins
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(program.router)

def handle_arguments():
    parser = argparse.ArgumentParser(description='Process server argument.')
    parser.add_argument('--server', action='store_true', help='Server argument')
    args = parser.parse_args()
    return args.server

async def dummy_function():
    pass

async def runChatbot():
    ## import the cli version of the chatbot
    from .chatInterface import ChatInterface
    from main.bot.bot_main import main
    chatbox = ChatInterface(callback=main, save=dummy_function, clear = dummy_function)
    await chatbox.start_chat()

if __name__ == "__main__":
    if handle_arguments() == True:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level='debug')
    else:
        asyncio.run(runChatbot())
