import glob
import importlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), "static")

moduleList = glob.glob("routes/*.py")
for module in moduleList:
    app.include_router(
        importlib.import_module(
            module.replace(".py", "").replace("\\", ".").replace("/", ".")
        ).router
    )
