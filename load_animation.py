PATHS = [
  "animation/rocket_frame_1.txt",
  "animation/rocket_frame_2.txt",
]

def load_frames():
  frames = []
  for path in PATHS:
    with open(path, "r") as f:
      frames.append(f.read())
  return frames
