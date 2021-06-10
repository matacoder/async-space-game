import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1


def draw(canvas):
    row, column = curses.window.getmaxyx(canvas)
    canvas.border()
    curses.curs_set(False)
    coroutines = []
    for i in range(50):
        pos_x = random.randint(5, row - 5)
        pos_y = random.randint(5, column - 5)
        symbol = random.choice('+*.:')
        coroutine = blink(canvas, pos_x, pos_y, symbol)
        coroutines.append(coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                time.sleep(TIC_TIMEOUT)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
    # while True:
    #     canvas.addstr(row, column, '*', curses.A_DIM)
    #     canvas.refresh()
    #     time.sleep(2)
    #     canvas.addstr(row, column, '*')
    #     canvas.refresh()
    #     time.sleep(0.3)
    #     canvas.addstr(row, column, '*', curses.A_BOLD)
    #     canvas.refresh()
    #     time.sleep(0.5)
    #     canvas.addstr(row, column, '*')
    #     canvas.refresh()
    #     time.sleep(0.3)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(1):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(1):
            await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)