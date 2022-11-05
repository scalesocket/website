#!/usr/bin/python3
from contextlib import suppress
from json import JSONDecodeError, loads, dumps
from sys import stdin, stdout


def main():
    stdin_events = map(parse_json, stdin)
    players = {}

    for event in stdin_events:
        op, id, data = parse_event(event)

        if op == "join":
            players[id] = (50, 50)
            send_event("join", id)
        elif op == "leave":
            del players[id]
            send_event("leave", id)
        elif op == "input":
            players[id] = (data.get("x", 0), data.get("y", 0))
            send_event("state", {"players": players})


def send_event(op: str, data: dict):
    # sending data is as easy as printing
    print(dumps({"op": op, "data": data}))


def parse_json(data):
    with suppress(JSONDecodeError):
        return loads(data)
    return None


def parse_event(event: dict):
    with suppress(KeyError):
        return event["op"], int(event["id"]), event.get("data")
    return None, None, None


if __name__ == "__main__":
    # ensure python output is not buffered
    stdout.reconfigure(line_buffering=True)
    main()
