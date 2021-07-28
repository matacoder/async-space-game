import time
import curses
import asyncio
import random
from fire_animation import fire
import game_scenario
from load_animation import load_frames
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size
import space_garbage
from physics import update_speed
from obstacles import Obstacle, has_collision, show_obstacles

DEBUG = False
TIC_TIMEOUT = 0.05
RESPONSIVENESS = 2
STARS = "+*.:"
STARS_COUNT = 5
SHIP_SPEED = 2
CANVAS_MARGIN = 2
GAME_OVER = load_frames(type_="game_over")

current_ship_frame = ""
current_ship_row = 0
current_ship_column = 0

row_speed = 0
column_speed = 0

game_difficulty = 1
current_phrase = "Look at the history of space exploration!"
year = 1955

coroutines = []
obstacles = []
obstacles_in_last_collisions = []


def generate_stars(canvas, total_rows, total_columns):
    """Generate stars' coroutines."""
    stars = []

    for _ in range(STARS_COUNT):
        pos_x = random.randint(CANVAS_MARGIN, total_rows - CANVAS_MARGIN)
        pos_y = random.randint(CANVAS_MARGIN, total_columns - CANVAS_MARGIN)
        symbol = random.choice(STARS)
        coroutine = blink(canvas, pos_x, pos_y, symbol)
        stars.append(coroutine)

    return stars


def initialize_ship(canvas, total_rows, total_columns):
    """First ship appearance in the center of canvas."""
    frames = load_frames()
    global current_ship_row
    global current_ship_column

    current_ship_row = total_rows // 2
    current_ship_column = total_columns // 2

    ship = draw_ship(canvas, current_ship_row, current_ship_column, frames)
    return ship


def fire_random_shot(canvas, position_rows, position_columns):
    """Fire random shot in the center of screen."""
    object_height, object_width = get_frame_size(current_ship_frame)
    shot = fire(
        canvas,
        position_rows,
        position_columns + object_width / 2,
        obstacles,
        obstacles_in_last_collisions,
        rows_speed=-1,
    )
    return shot


async def fill_orbit_with_garbage(canvas, total_columns):
    """Garbage generator coroutine."""
    global coroutines
    garbage = load_frames("garbage")
    while True:
        garbage_frame = random.choice(garbage)
        column = random.choice(range(1, total_columns))
        random_garbage = space_garbage.fly_garbage(
            canvas,
            column,
            garbage_frame,
            obstacles,
            obstacles_in_last_collisions,
            speed=0.5,
        )
        coroutines.append(random_garbage)
        await sleep(game_scenario.get_garbage_delay_tics(year))


async def show_history_text(canvas):
    """Display this year in history info."""
    global current_phrase
    global year
    while True:
        current_phrase = game_scenario.PHRASES.get(year, current_phrase)
        draw_frame(canvas, 1, 2, f"{year}: {current_phrase}")
        await sleep(int(1 / TIC_TIMEOUT))
        draw_frame(canvas, 1, 2, f"{year}: {current_phrase}", negative=True)
        year += 1


def draw(canvas):
    """Main event loop."""

    curses.curs_set(False)
    canvas.nodelay(True)
    total_rows, total_columns = curses.window.getmaxyx(canvas)

    global coroutines

    stars = generate_stars(canvas, total_rows, total_columns)
    coroutines += stars

    ship = initialize_ship(canvas, total_rows, total_columns)
    coroutines.append(ship)

    garbage_generator = fill_orbit_with_garbage(canvas, total_columns)
    coroutines.append(garbage_generator)

    # Show rectangles around obstacles (debug mode only).
    if DEBUG:
        coroutines.append(show_obstacles(canvas, obstacles))

    coroutines.append(show_history_text(canvas))

    game_speed = TIC_TIMEOUT / len(coroutines)

    while True:
        canvas.border()

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                pause_game_with_responsive_controls(game_speed, canvas)
            except StopIteration:
                coroutines.remove(coroutine)
                game_speed = TIC_TIMEOUT / len(coroutines)
        if len(coroutines) == 0:
            break

        canvas.refresh()


def pause_game_with_responsive_controls(game_speed, canvas):
    """Increased game RESPONSIVENESS for controls."""
    for _ in range(RESPONSIVENESS):
        read_controls_and_move_ship(canvas)
        time.sleep(game_speed / RESPONSIVENESS)


async def sleep(tics=1):
    """Help waiting for other coroutines."""
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol="*"):
    """Default star animation with randomizer."""
    await sleep(random.randint(0, 30))
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
        await sleep(2)


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
    global current_ship_row
    global current_ship_column
    global coroutines
    global row_speed
    global column_speed

    rows_direction, columns_direction, space_bar = read_controls(canvas)

    row_speed, column_speed = update_speed(
        row_speed, column_speed, rows_direction, columns_direction
    )

    if space_bar and year >= 2020:
        shot = fire_random_shot(canvas, current_ship_row, current_ship_column)
        coroutines.append(shot)

    if rows_direction or columns_direction or row_speed or column_speed:
        erase_ship_frame(canvas)
        current_ship_row += row_speed * SHIP_SPEED
        current_ship_column += column_speed * SHIP_SPEED

        current_ship_row, current_ship_column = check_object_size(
            current_ship_row, current_ship_column, current_ship_frame, canvas
        )
        check_game_over(canvas)

        draw_frame(canvas, current_ship_row, current_ship_column, current_ship_frame)


def check_game_over(canvas):
    """Check collisions with star ship and show Game Over message."""
    for obstacle in obstacles:
        if has_collision(
            (
                obstacle.row,
                obstacle.column,
            ),
            (
                obstacle.rows_size,
                obstacle.columns_size,
            ),
            (current_ship_row, current_ship_column),
        ):
            obstacles_in_last_collisions.append(obstacle)
            object_height, object_width = get_frame_size(GAME_OVER[0])
            total_rows, total_columns = curses.window.getmaxyx(canvas)
            draw_frame(
                canvas,
                (total_rows - object_height) // 2,
                (total_columns - object_width) // 2,
                GAME_OVER[0],
            )

            canvas.nodelay(False)
            # Press any key to continue:
            pressed_key_code = canvas.getch()
            if pressed_key_code:
                draw_frame(
                    canvas,
                    (total_rows - object_height) // 2,
                    (total_columns - object_width) // 2,
                    GAME_OVER[0],
                    negative=True,
                )
                canvas.nodelay(True)


def check_object_size(row, column, frame, canvas):
    """Check if object is trying to move outside of canvas."""
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
