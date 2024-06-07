import uvicorn
from fastapi import FastAPI, APIRouter
import argparse
from main.bot.api import router
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with the appropriate origins
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

def handle_arguments():
    parser = argparse.ArgumentParser(description='Process server argument.')
    parser.add_argument('--server', action='store_true', help='Server argument')
    args = parser.parse_args()
    return args.server

async def dummy_function():
    pass

async def notMain():
    if handle_arguments() == True:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        ## import the cli version of the chatbot
        from .chatInterface import ChatInterface
        from main.bot.bot_main import main
        chatbox = ChatInterface(callback=main, save=dummy_function, clear = dummy_function)
        await chatbox.start_chat()

if __name__ == "__main__":
    asyncio.run(notMain())
