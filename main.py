import asyncio
import glob
import importlib
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.aki import deleteCheck
from vocasong import SongService


async def musicReload():
    while True:
        if datetime.now().minute == 0:
            await asyncio.to_thread(SongService.loadSongs)
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task1 = asyncio.create_task(musicReload())
    task2 = asyncio.create_task(deleteCheck())
    yield
    task1.cancel()
    task2.cancel()


app = FastAPI(
    lifespan=lifespan,
    redoc_url=None,
    docs_url=None,
    openapi_url=None,
    swagger_ui_oauth2_redirect_url=None,
)
app.mount("/static", StaticFiles(directory="static"), "static")

moduleList = glob.glob("routes/*.py")
for module in moduleList:
    app.include_router(
        importlib.import_module(
            module.replace(".py", "").replace("\\", ".").replace("/", ".")
        ).router
    )
