from curses_tools import draw_frame, get_frame_size
import asyncio
import main
from obstacles import Obstacle
import uuid


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    object_height, object_width = get_frame_size(garbage_frame)

    uid = str(uuid.uuid4())

    row = 0

    while row < rows_number:
        main.obstacles.append(
            Obstacle(
                row=row,
                column=column,
                rows_size=object_height,
                columns_size=object_width,
                uid=uid,
            )
        )
        draw_frame(canvas, row, column, garbage_frame)

        await asyncio.sleep(0)
        for i, o in enumerate(main.obstacles):
            if o.uid == uid:
                del o[i]
                break
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
