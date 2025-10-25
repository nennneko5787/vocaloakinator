from vocasong import Choices, SongService, VocaSongAki


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


SongService.loadSongs()

aki = VocaSongAki()

aki.start()

while not aki.end:
    aki.ask()

    print(aki.question)

    while not (choice := strToChoices(input("[y/py/idk/pn/n]: "))):
        pass

    aki.answer(choice)

    if aki.answerSong:
        print(
            f"The song is: {aki.answerSong.name} by {aki.answerSong.musician} (released on {aki.answerSong.releasedAt.year})"
        )
