from vocasong import VocaSongAki

aki = VocaSongAki()

aki.start()

while not aki.end:
    aki.ask()

    print(aki.question)

    aki.answer(not input("[Y/n]: ") == "n")

    if aki.answerSong:
        print(
            f"The song is: {aki.answerSong.name} by {aki.answerSong.musician} (released on {aki.answerSong.releasedAt.year})"
        )
