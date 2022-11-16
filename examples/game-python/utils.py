from __future__ import annotations
import asyncio
from contextlib import suppress
from json import JSONDecodeError, loads
from dataclasses import dataclass, field
from collections import namedtuple
from functools import wraps
from contextlib import suppress
from time import process_time
from json import JSONEncoder
from typing import Any

Point = namedtuple("Point", ["x", "y"], defaults=(0, 0))


def clamp(n: int, smallest: int, largest: int) -> int:
    return max(smallest, min(n, largest))


def clamp_point(p: Point, smallest_x, largest_x, smallest_y, largest_y) -> Point:
    return Point(clamp(p.x, smallest_x, largest_x), clamp(p.y, smallest_y, largest_y))


@dataclass
class Vec:
    x: int = field(default=0)
    y: int = field(default=0)

    def to_point(self) -> Point:
        return Point(self.x, self.y)

    @classmethod
    def from_point(cls, point: Point) -> "Vec":
        return cls(point.x, point.y)

    @classmethod
    def from_dict(cls, data: dict) -> "Vec":
        return cls(data.get("x", 0), data.get("y", 0))

    def clamp(self, smallest_x: int, largest_x: int, smallest_y: int, largest_y: int):
        return Vec(
            clamp(self.x, smallest_x, largest_x),
            clamp(self.y, smallest_y, largest_y)
            # max(smallest_x, min(self.x, largest_x)), max(smallest_y, min(self.y, )),
        )

    def int(self):
        return Vec(int(self.x), int(self.y))

    def __add__(self, other: "Vec"):
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec"):
        return Vec(self.x - other.x, self.y - other.y)

    def __truediv__(self, other: Vec | int | float):
        if isinstance(other, Vec):
            return Vec(self.x / other.x, self.y / other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return Vec(self.x / other, self.y / other)
        else:
            return NotImplemented

    def __floordiv__(self, other: Vec | int | float):
        return (self / other).int()

    def __eq__(self, other):
        if isinstance(other, Vec):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented


def with_interval(interval: float):
    """Run method with specified interval."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                start = process_time()
                await func(*args, **kwargs)
                elapsed = process_time() - start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)

        return wrapper

    return decorator


def parse_json(data: bytes):
    with suppress(JSONDecodeError, UnicodeDecodeError):
        return loads(data.decode("utf-8"))
    return None


Event = tuple[str, int, dict] | tuple[str, int, dict] | tuple[str, int]


# def parse_event(event: dict) -> Event | None:
#     with suppress(KeyError, TypeError):
#         match event:
#             case {"type": type, "id": id, "data": data}:
#                 return str(type), int(id), dict(data)
#             case {"type": type, "id": id}:
#                 return str(type), int(id)
#             case _:
#                 return None

# with suppress(KeyError, TypeError):
#     type, id = str(event["type"]), int(event["id"])

#     if data := event.get("data"):
#         return type, id, dict(data)
#     else:
#         return type, id

# return None

# def __post_init__(self):
#     pass


class DataclassEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Vec):
            return [o.x, o.y]
        # elif isinstance(o, dataclass):
        return o.__dict__
        # if isinstance(obj, Person):
        #     return o.__dict__
        # return json.JSONEncoder.default(self, obj)

    @classmethod
    def dumps(cls, o: Any) -> str:
        return cls().encode(o)


# encoder = DataclassEncoder()


# def dumps_dataclass(o: Any) -> str:
#     return encoder.encode(o)

# @dataclass
# class MixinObj:
#     def json(self) -> str:
#         encoder = DataclassEncoder()


#         return encoder.encode(self)
