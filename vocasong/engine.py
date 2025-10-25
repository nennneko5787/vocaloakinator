import time
from enum import Enum
from typing import Any, Union

import numpy as np
import pandas as pd

from .song import Song, SongService


class Choices(Enum):
    YES = 1.0
    PROBABLY_YES = 0.75
    IDK = 0.5
    PROBABLY_NO = 0.25
    NO = 0.0


class VocaSongAki:
    def __init__(self):
        self.selectedColumn: Union[int, str] = None
        self.selectedData: pd.DataFrame = None
        self.purity: pd.Series[Any] = None

        self.end = False
        self.question: str = None
        self.answerSong: Song = None
        self.prevQuestions: set[str] = set()

        self.initialCount: int = 0
        self.progressValue: float = 0.0

        self.lastUpdatedAt = time.time()

    def ask(self):
        if self.data.shape[0] == 1:
            self.answerSong = SongService.getSongById(self.data.iloc[0, 0])
            self.end = True
            return

        columns = self.data.columns[1:]
        entropyValues = {}

        for col in columns:
            if col in self.prevQuestions:
                continue
            p = self.data[col].mean()
            if p in [0, 1]:
                continue
            entropy = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
            entropyValues[col] = entropy

        if not entropyValues:
            self.end = True
            return

        self.selectedColumn = max(entropyValues, key=entropyValues.get)
        self.prevQuestions.add(self.selectedColumn)
        self.question = f"その曲{self.selectedColumn}？"

        self._updateProgress()

    def answer(self, choice: Choices):
        targetValue = choice.value
        colValues = self.data[self.selectedColumn].astype(float)
        similarity = 1 - np.abs(colValues - targetValue)

        if choice == Choices.IDK:
            threshold = np.quantile(similarity, 0.25)
        elif choice in (Choices.PROBABLY_YES, Choices.PROBABLY_NO):
            threshold = np.median(similarity)
        else:
            threshold = similarity.mean()

        self.selectedData = self.data[similarity >= threshold]

        if self.selectedData.shape[0] == 1:
            songId = self.selectedData.iloc[0, 0]
            self.answerSong = SongService.getSongById(songId)
            self.end = True

        self.data = self.selectedData.reset_index(drop=True)
        self.selectedData = None

        self._updateProgress()

    def start(self):
        self.data = SongService.dataFrame.copy()
        self.initialCount = len(self.data)
        self.data.replace(
            {np.int64(True): np.float64(1.0), np.int64(False): np.float64(1.0)},
            inplace=True,
        )

    def _updateProgress(self):
        remainingRatio = len(self.data) / self.initialCount
        questionRatio = len(self.prevQuestions) / max(
            1, len(SongService.dataFrame.columns) - 1
        )
        self.progressValue = min(1.0, (1 - remainingRatio) * 0.7 + questionRatio * 0.3)

        self.lastUpdatedAt = time.time()

    @property
    def progress(self) -> float:
        return round(self.progressValue, 3)
