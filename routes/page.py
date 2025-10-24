from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates("pages")


@router.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/play")
def play(request: Request):
    return templates.TemplateResponse(request, "play.html")
