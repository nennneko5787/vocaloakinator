import glob
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd
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
    YUKARI = "結月ゆかり"


class SongQuestions(BaseModel):
    mythology: bool = False  # 神話入りしているか？なお神話入りの基準はニコニコ動画で行うものとする(YT基準の判定も後で作るかも？)
    legend: bool = False  # 伝説入りしているか？なお伝説入りの基準は(ry
    addition: Dict[str, bool]


class Song(BaseModel):
    id: str
    name: str
    releasedAt: datetime  # ニコニコでは正確な秒数まで取れるのでdatetimeで良い ?responseType=json で返ってきたjsonのregisteredAtにある。検索してみると良い
    singers: List[Singers]
    musician: str
    link: str
    questions: SongQuestions


class SongService:
    songs: List[Song] = []
    questions: Dict[str, Optional[str]] = {}
    questions["は神話入りしていますか"] = "mythology"
    questions["は伝説入りしていますか"] = "legend"
    dataFrame: pd.DataFrame = None

    for singer in Singers:
        questions[f"は{singer.value}が歌っていますか"] = None

    @classmethod
    def loadSongs(cls):
        cls.songs: List[Song] = []
        cls.questions: Dict[str, Optional[str]] = {}
        cls.questions["は神話入りしていますか"] = "mythology"
        cls.questions["は伝説入りしていますか"] = "legend"
        cls.dataFrame: pd.DataFrame = None

        for singer in Singers:
            cls.questions[f"は{singer.value}が歌っていますか"] = None

        fileList = glob.glob("datas/songs/**/*.json")
        for file in fileList:
            _, _, musician, id = file.replace("\\", "/").split("/")
            id = id.removesuffix(".json")

            with open(file, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                data["id"] = f"{musician}-{id}"

                song = Song.model_validate(data)

                for question in song.questions.addition.keys():
                    cls.questions[question] = None

                cls.questions[f"は{song.releasedAt.year}年にリリースされましたか"] = (
                    song.releasedAt.year
                )

                cls.questions[f"のタイトルは{song.name[0]}から始まりますか"] = None
                cls.questions[f"は{song.musician}さんによる楽曲ですか"] = None

                cls.songs.append(song)

        data = []

        for song in cls.songs:
            songDict = {"name": song.id}
            dumpedQuestion = song.questions.model_dump()

            for questionRawName, questionId in cls.questions.items():
                if questionId is None:
                    if questionRawName == f"のタイトルは{song.name[0]}から始まりますか":
                        songDict[questionRawName] = True
                        continue

                    if questionRawName == f"は{song.musician}さんによる楽曲ですか":
                        songDict[questionRawName] = True
                        continue

                    singerMatched = False
                    for singer in Singers:
                        if questionRawName == f"は{singer.value}が歌っていますか":
                            songDict[questionRawName] = singer in song.singers
                            singerMatched = True
                            break
                    if singerMatched:
                        continue

                    songDict[questionRawName] = song.questions.addition.get(
                        questionRawName, False
                    )
                    continue

                if isinstance(questionId, int):
                    songDict[questionRawName] = questionId == song.releasedAt.year
                    continue

                songDict[questionRawName] = dumpedQuestion[questionId]

            data.append(songDict)

        cls.dataFrame = pd.DataFrame(data)

    @classmethod
    def getSongById(cls, id: str) -> Song:
        for song in cls.songs:
            if song.id == id:
                return song

        raise ValueError()
