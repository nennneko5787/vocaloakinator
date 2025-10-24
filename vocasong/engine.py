from typing import Any, Union

import numpy as np
import pandas as pd

from .song import Singers, Song, getSongById, loadSongs, questions, songs


class VocaSongAki:
    def __init__(self):
        self.selectedColumn: Union[int, str] = None
        self.selectedData: pd.DataFrame = None
        self.data: pd.DataFrame = None
        self.purity: pd.Series[Any] = None

        self.end = False
        self.question: str = None
        self.answerSong: Song = None

    def ask(self):
        self.purity = (
            self.data.iloc[:, 1:].sum()
            - np.full(self.data.shape[1] - 1, self.data.shape[0] / 2)
        ).abs()

        self.selectedColumn = self.purity.idxmin()
        self.question = f"その曲{self.selectedColumn}？"

    def answer(self, choice: bool):
        if choice:
            self.selectedData = self.data[self.data[self.selectedColumn]]
        else:
            self.selectedData = self.data[~self.data[self.selectedColumn]]

        if self.selectedData.shape[0] == 1:
            self.answerSong = getSongById(self.selectedData.iloc[0, 0])
            self.end = True

        self.data = self.selectedData.reset_index(drop=True)
        self.selectedData = None

    def start(self):
        data = []

        if len(songs) <= 0:
            loadSongs()

        for song in songs:
            songDict = {"name": song.id}
            dumpedQuestion = song.questions.model_dump()

            for questionRawName, questionId in questions.items():
                if questionId is None:
                    if questionRawName == f"のタイトルは{song.name[0]}から始まりますか":
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

        self.data = pd.DataFrame(data)
