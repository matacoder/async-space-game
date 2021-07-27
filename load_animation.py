PATHS = {
    "ship": [
        "animation/rocket_frame_1.txt",
        "animation/rocket_frame_2.txt",
    ],
    "garbage": [
        "animation/duck.txt",
        "animation/hubble.txt",
        "animation/lamp.txt",
        "animation/trash_large.txt",
        "animation/trash_small.txt",
        "animation/trash_xl.txt",
    ],
    "game_over": ["animation/game_over.txt"],
}


def load_frames(type_="ship"):
    frames = []
    for path in PATHS[type_]:
        with open(path, "r") as f:
            frames.append(f.read())
    return frames
