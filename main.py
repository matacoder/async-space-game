import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1
STARS = '+*.:'

def draw(canvas):
    row, column = curses.window.getmaxyx(canvas)
    canvas.border()
    curses.curs_set(False)
    coroutines = []
    for i in range(200):
        pos_x = random.randint(2, row - 2)
        pos_y = random.randint(2, column - 2)
        symbol = random.choice(STARS)
        coroutine = blink(canvas, pos_x, pos_y, symbol)
        coroutines.append(coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                # time.sleep(TIC_TIMEOUT)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        
async def sleep(tic=1):
    for _ in range(tic*random.randint(30, 50)):
        await asyncio.sleep(0)

async def blink(canvas, row, column, symbol='*'):
    while True:
        
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)