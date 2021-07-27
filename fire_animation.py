import asyncio
import curses

from obstacles import has_collision


async def fire(
    canvas,
    start_row,
    start_column,
    obstacles,
    obstacles_in_last_collisions,
    rows_speed=-0.3,
    columns_speed=0,
):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        row = round(row)
        column = round(column)
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")

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
                (row, column),
            ):
                obstacles_in_last_collisions.append(obstacle)
                return

        row += rows_speed
        column += columns_speed
