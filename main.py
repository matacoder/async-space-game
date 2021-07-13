import time
import curses
import asyncio
import random
from fire_animation import fire
from load_animation import load_frames
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size

TIC_TIMEOUT = 0.05
STARS = "+*.:"
STARS_COUNT = 100
SHIP_SPEED = 2
CANVAS_MARGIN = 2


current_ship_frame = ""
current_ship_row = 0
current_ship_column = 0


def generate_stars(canvas):
    """Generate stars' coroutines."""
    stars = []

    total_rows, total_columns = curses.window.getmaxyx(canvas)

    for _ in range(STARS_COUNT):
        pos_x = random.randint(CANVAS_MARGIN, total_rows - CANVAS_MARGIN)
        pos_y = random.randint(CANVAS_MARGIN, total_columns - CANVAS_MARGIN)
        symbol = random.choice(STARS)
        coroutine = blink(canvas, pos_x, pos_y, symbol)
        stars.append(coroutine)

    return stars


def draw(canvas):
    """Main event loop."""

    curses.curs_set(False)
    canvas.nodelay(True)

    coroutines = []

    stars = generate_stars(canvas)
    coroutines += stars


    total_rows, total_columns = curses.window.getmaxyx(canvas)
    shot = fire(canvas, total_rows - CANVAS_MARGIN, total_columns // 2)
    coroutines.append(shot)


    frames = load_frames()
    global current_ship_row
    global current_ship_column

    current_ship_row = total_rows // 2    
    current_ship_column = total_columns // 2

    ship = draw_ship(canvas, current_ship_row, current_ship_column, frames)
    coroutines.append(ship)

    game_speed = TIC_TIMEOUT / len(coroutines)

    while True:
        canvas.border()
        for coroutine in coroutines.copy():
            try:
                read_controls_and_move_ship(canvas)
                coroutine.send(None)
                time.sleep(game_speed)
            except StopIteration:
                coroutines.remove(coroutine)
                game_speed = TIC_TIMEOUT / len(coroutines)
        if len(coroutines) == 0:
            break
        canvas.refresh()


async def sleep(tic=1):
    """Randomize star blinking."""
    for _ in range(tic + random.randint(0, 10)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol="*"):
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
    """Ship animation."""
    global current_ship_frame
    for frame in cycle(frames):
        erase_ship_frame(canvas)
        draw_frame(canvas, current_ship_row, current_ship_column, frame)
        current_ship_frame = frame

        for _ in range(2):
            await asyncio.sleep(0)


def erase_ship_frame(canvas):
    """Remove current ship from canvas."""
    if current_ship_frame:
        draw_frame(
            canvas,
            current_ship_row,
            current_ship_column,
            current_ship_frame,
            negative=True,
        )

def read_controls_and_move_ship(canvas):
    """Read controls and immediately move ship."""
    rows_direction, columns_direction, _ = read_controls(canvas)
    if rows_direction or columns_direction:
        erase_ship_frame(canvas)
        
        global current_ship_row
        global current_ship_column

        current_ship_row += rows_direction * SHIP_SPEED
        current_ship_column += columns_direction * SHIP_SPEED

        current_ship_row, current_ship_column = check_object_size(
            current_ship_row, current_ship_column, current_ship_frame, canvas
        )
        
        draw_frame(canvas, current_ship_row, current_ship_column, current_ship_frame)


def check_object_size(row, column, frame, canvas):
    """Check if object is trying to move outside of canves."""
    object_height, object_width = get_frame_size(frame)
    canvas_height, canvas_width = canvas.getmaxyx()
    row_limit = canvas_height - object_height - CANVAS_MARGIN
    column_limit = canvas_width - object_width - CANVAS_MARGIN
    if row < CANVAS_MARGIN:
        row = CANVAS_MARGIN
    elif row > row_limit:
        row = row_limit
    if column < CANVAS_MARGIN:
        column = CANVAS_MARGIN
    elif column > column_limit:
        column = column_limit
    return row, column


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
