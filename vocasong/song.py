import glob
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import orjson
from pydantic import BaseModel


class Singers(Enum):
    MIKU = "初音ミク"
    RIN = "鏡音リン"
    LEN = "鏡音レン"
    LUKA = "巡音ルカ"
    KAITO = "KAITO"
    MEIKO = "MEIKO"
    KAFU = "可不"
    GUMI = "GUMI"
    IA = "IA"
    FLOWER = "flower"
    TETO = "重音テト"
    SELF = "ボカロP本人"


class SongQuestions(BaseModel):
    mythology: bool  # 神話入りしているか？なお神話入りの基準はニコニコ動画で行うものとする(YT基準の判定も後で作るかも？)
    addition: Dict[str, bool]


class Song(BaseModel):
    id: str
    name: str
    releasedAt: datetime  # ニコニコでは正確な秒数まで取れるのでdatetimeで良い ?responseType=json で返ってきたjsonのregisteredAtにある。検索してみると良い
    singers: List[Singers]
    musician: str
    link: str
    questions: SongQuestions


songs: List[Song] = []
questions: Dict[str, Optional[str]] = {}
questions["は神話入りしていますか"] = "mythology"

for singer in Singers:
    questions[f"は{singer.value}が歌っていますか"] = None


def loadSongs():
    fileList = glob.glob("datas/songs/**/*.json")
    for file in fileList:
        _, _, musician, id = file.replace("\\", "/").split("/")
        id = id.removesuffix(".json")

        with open(file, "rb") as f:
            data = orjson.loads(f.read())
            data["id"] = f"{musician}-{id}"

            song = Song.model_validate(data)

            for question in song.questions.addition.keys():
                questions[question] = None

            questions[f"は{song.releasedAt.year}年にリリースされましたか"] = (
                song.releasedAt.year
            )

            questions[f"のタイトルは{song.name[0]}から始まりますか"] = None

            songs.append(song)


def getSongById(id: str) -> Song:
    for song in songs:
        if song.id == id:
            return song

    raise ValueError()
