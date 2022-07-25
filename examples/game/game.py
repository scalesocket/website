#! /usr/bin/python3
from contextlib import suppress
from dataclasses import dataclass, field
from json import JSONDecodeError, loads, dumps
from sys import stdin, stdout
from operator import itemgetter


def main():
    state = State()
    # parse incoming events from stdin
    for event in map(parse_json, stdin):
        try:
            state.handle_event(event)
        except Exception as err:
            # on error, send error to client by printing
            print(dumps({"error": err.__class__.__name__}))
        else:
            # on succes, send state to client by printing
            print(dumps({"op": "state", "data": state.__dict__}))


@dataclass
class State:
    players: dict = field(default_factory=dict)

    def handle_event(self, ev: dict):
        ev = {"op": None, "id": None, "data": None, **ev}
        op, id, data = itemgetter("op", "id", "data")(ev)
        getattr(self, op)(id, data)

    def input(self, id: int, data: dict):
        pos = (data.get("x", 0), data.get("y", 0))
        self.players[id] = pos

    def join(self, id: int, data: None):
        # send join info to clients
        print(dumps({"op": "join", "data": id}))
        self.players[id] = (50, 50)

    def leave(self, id: int, data: None):
        # inform clients about leave
        print(dumps({"op": "leave", "data": id}))
        del self.players[id]


def parse_json(data):
    with suppress(JSONDecodeError):
        return loads(data)
    return None


if __name__ == "__main__":
    # ensure python output is not buffered
    stdout.reconfigure(line_buffering=True)
    main()
