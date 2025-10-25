import asyncio
import os
import secrets
import time
from typing import Dict, Optional

import dotenv
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Response
from pydantic import BaseModel

from vocasong import Choices, Singers, SongService, VocaSongAki

dotenv.load_dotenv()

router = APIRouter()
games: Dict[str, VocaSongAki] = {}


async def deleteCheck():
    while True:
        for key in list(games.keys()):
            if games[key].lastUpdatedAt + 3600 <= time.time():
                del games[key]
        await asyncio.sleep(60)


@router.get("/api/aki")
def akiStatus():
    return {
        "songs": len(SongService.songs),
        "questions": len(SongService.questions),
        "singers": len(Singers),
    }


class AkiStartRequest(BaseModel):
    cfToken: Optional[str] = None


@router.post("/api/aki/start")
async def startAki(httpResponse: Response, model: AkiStartRequest):
    if not model.cfToken:
        raise HTTPException(403)

    async with httpx.AsyncClient() as http:
        try:
            response = await http.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                json={
                    "secret": os.getenv("tsSecret"),
                    "response": model.cfToken,
                },
                timeout=10,
            )

            jsonData: Dict[str, str] = response.json()

            if not jsonData.get("success", False):
                raise HTTPException(403)

        except httpx.RequestError as e:
            httpResponse.status_code = 500

            print(f"Turnstile validation error: {e}")
            return {
                "detail": "START_FAILED",
            }

    token = secrets.token_hex(32)
    games[token] = VocaSongAki()

    games[token].start()
    games[token].ask()

    response.status_code = 201
    return {
        "detail": "START_SUCCESS",
        "token": token,
        "question": games[token].question,
        "progress": games[token].progress,
    }


def strToChoices(choice: str) -> Choices:
    match choice:
        case "y":
            return Choices.YES
        case "py":
            return Choices.PROBABLY_YES
        case "idk":
            return Choices.IDK
        case "pn":
            return Choices.PROBABLY_NO
        case "n":
            return Choices.NO

    return False


class AkiAnswerRequest(BaseModel):
    token: Optional[str] = None
    answer: Optional[str] = None


@router.post("/api/aki/answer")
def answerAki(backgroundTasks: BackgroundTasks, model: AkiAnswerRequest):
    if not model.token:
        raise HTTPException(403)
    if model.token not in games:
        raise HTTPException(403)

    choice = strToChoices(model.answer)
    if not choice:
        raise HTTPException(403)

    games[model.token].answer(choice)

    if games[model.token].answerSong:

        def delete():
            del games[model.token]

        backgroundTasks.add_task(delete)

        return {"detail": "SONG_MATCHED", "song": games[model.token].answerSong}
    else:
        games[model.token].ask()
        return {
            "detail": "SONG_DOESNT_MATCH",
            "question": games[model.token].question,
            "progress": games[model.token].progress,
        }
