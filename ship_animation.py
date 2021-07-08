ROUTES = [
  "animation/rocket_frame_1.txt",
  "animation/rocket_frame_2.txt",
]

def load_frames():
  frames = []
  for route in ROUTES:
    with open(route, "r") as f:
      frames.append(f.read())
  return frames
