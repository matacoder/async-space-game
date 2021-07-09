import time
import curses
import asyncio
import random
from fire_animation import fire
from ship_animation import load_frames
from itertools import cycle
from curses_tools import draw_frame

TIC_TIMEOUT = 0.1
STARS = '+*.:'
STARS_COUNT = 100


def generate_stars(canvas):
    """Generate stars' coroutines."""
    stars = []
    # Get screen size to draw inside it
    row, column = curses.window.getmaxyx(canvas)
    for i in range(STARS_COUNT):
        pos_x = random.randint(2, row - 2)
        pos_y = random.randint(2, column - 2)
        symbol = random.choice(STARS)
        coroutine = blink(canvas, pos_x, pos_y, symbol)
        stars.append(coroutine)
    return stars


def draw(canvas):
    """Main event loop."""

    # Turn off blinking cursor
    curses.curs_set(False)

    # Main array of game
    coroutines = []

    # Give me some stars
    stars = generate_stars(canvas)
    coroutines += stars

    # Fire ramdom shot
    row, column = curses.window.getmaxyx(canvas)
    shot = fire(canvas, row - 1, column // 2)
    coroutines.append(shot)

    # Add ship in the center
    frames = load_frames()
    ship = draw_ship(canvas, row // 2, column // 2, frames)
    coroutines.append(ship)

    # Now game speed doesn't depend on CPU
    fix_game_speed = TIC_TIMEOUT / len(coroutines)

    # Main event loop thoght all coroutines
    while True:
        canvas.border()
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                time.sleep(fix_game_speed)
            except StopIteration:
                coroutines.remove(coroutine)
                fix_game_speed = TIC_TIMEOUT / len(coroutines)
        if len(coroutines) == 0:
            break
        canvas.refresh()


async def sleep(tic=1):
    """Randomize star blinking."""
    for _ in range(tic + random.randint(0, 10)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    """Default star animation."""
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)
        canvas.addstr(row, column, symbol)
        await sleep(3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)
        canvas.addstr(row, column, symbol)
        await sleep(3)


async def draw_ship(canvas, row, column, frames):
    previous_frame = ""
    for frame in cycle(frames):
        # стираем предыдущий кадр, прежде чем рисовать новый
        if previous_frame:
            draw_frame(canvas, row, column, previous_frame, negative=True)
        draw_frame(canvas, row, column, frame)
        previous_frame = frame
        await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
