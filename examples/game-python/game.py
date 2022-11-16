#!/usr/bin/python3
import asyncio
from asyncio import StreamReader, StreamWriter
from aioconsole import get_standard_streams
from contextlib import suppress
from sys import stderr
from state import State
from utils import Vec, with_interval, parse_json, DataclassEncoder


async def main():
    reader, writer = await get_standard_streams()
    state = State(players={}, items={})

    await asyncio.gather(
        update_input(reader, state),
        update_game(writer, state),
    )


async def update_input(reader: StreamReader, state: State):
    async for line in reader:
        event = parse_json(line)
        match event:
            case {"type": "input", "id": id, "data": data}:
                pos = Vec.from_dict(data) // 32
                if state.get_player(pos):
                    state.set_player_explosive(id, pos)
                else:
                    state.set_player_target_pos(id, pos)
            case {"type": "join", "id": id}:
                state.add_player(id)
            case {"type": "leave", "id": id}:
                state.remove_player(id)


@with_interval(0.25)
async def update_game(writer: StreamWriter, state: State):
    state.update()
    line = DataclassEncoder.dumps({"type": "state", "data": state}) + "\n"
    writer.write(line.encode())


if __name__ == "__main__":
    print("round started", file=stderr)
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
