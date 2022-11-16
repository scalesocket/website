from dataclasses import dataclass, field
from contextlib import suppress
from utils import Vec
from typing import Optional
from sys import stderr

PLAYER_HEALTH = 2
EXPLOSION_ENERGY = 5
EXPLOSIVE_TTL = 12
WALL_EMPTY = 0
WALL_SOFT = 1
WALL_HARD = 2


@dataclass
class Map:
    data: list[list[int]]
    width: int
    height: int

    def get_wall(self, pos: Vec) -> int | None:
        with suppress(IndexError):
            wall = self.data[pos.y][pos.x]
        return wall if wall != WALL_EMPTY else None

    def set_wall(self, pos: Vec, value: int):
        with suppress(IndexError):
            self.data[pos.y][pos.x] = value

    def start_pos(self, idx: Optional[int] = None) -> Vec:
        positions = [Vec(1, 1), Vec(9, 9), Vec(1, 9), Vec(9, 1)]
        return positions[idx % 4]

    @classmethod
    def default(cls):
        return cls(
            width=10,
            height=10,
            data=[
                [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                [2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
                [2, 0, 2, 1, 2, 1, 2, 1, 2, 0, 2],
                [2, 0, 1, 1, 1, 1, 1, 1, 1, 0, 2],
                [2, 0, 2, 1, 2, 1, 2, 1, 2, 0, 2],
                [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
                [2, 0, 2, 1, 2, 1, 2, 1, 2, 0, 2],
                [2, 0, 1, 1, 1, 1, 1, 1, 1, 0, 2],
                [2, 0, 2, 1, 2, 1, 2, 1, 2, 0, 2],
                [2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
                [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            ],
        )


@dataclass
class Player:
    id: int
    pos: Vec
    target_pos: Vec = field(default_factory=Vec)
    health: int = field(default=PLAYER_HEALTH)
    explosives: int = field(default=1)

    def is_dead(self) -> bool:
        return self.health <= 0


@dataclass
class Item:
    id: int
    type: str
    pos: Vec
    ttl: int
    player: Optional[int] = field(default=None)

    def update(self):
        self.ttl -= 1

    def is_dead(self) -> bool:
        return self.ttl <= 0


@dataclass
class State:
    players: dict[int, Player] = field(default_factory=dict)
    items: dict[int, Item] = field(default_factory=dict)
    map: Map = field(default_factory=Map.default)
    items_counter = 0

    def add_player(self, id: int):
        start_pos = self.map.start_pos(id)
        self.players[id] = Player(id, pos=start_pos, target_pos=start_pos)

    def remove_player(self, id: int):
        del self.players[id]

    def set_player_explosive(self, id: int, pos: Vec):
        if player := self.get_player(pos):
            if player.id == id and player.explosives:
                self.add_item("explosive", pos, player.id, ttl=EXPLOSIVE_TTL)
                player.explosives -= 1

    def set_player_target_pos(self, id: int, pos: Vec):
        if player := self.players.get(id):
            dist = pos - player.pos
            if abs(dist.x) > abs(dist.y):
                new_pos = Vec(pos.x, player.pos.y)
            else:
                new_pos = Vec(player.pos.x, pos.y)

            player.target_pos = new_pos.clamp(0, self.map.width, 0, self.map.height)

    def get_player(self, pos: Vec) -> Player | None:
        return next(
            (player for player in self.players.values() if player.pos == pos),
            None,
        )

    def add_item(self, type: str, pos: Vec, player: Optional[int] = None, ttl: int = 5):
        id = self.items_counter
        self.items[id] = Item(type=type, pos=pos, id=id, player=player, ttl=ttl)
        self.items_counter += 1

    def do_explosion(self, pos: Vec):
        hits = self._calculate_explosion(pos)
        for pos in hits:
            self.map.set_wall(pos, WALL_EMPTY)
            self.add_item("fire", pos, ttl=1)

    def _calculate_explosion(self, start_pos: Vec) -> list[Vec]:
        directions = [Vec(0, 1), Vec(0, -1), Vec(1, 0), Vec(-1, 0)]
        hits = [start_pos]
        for step in directions:
            pos = start_pos + step
            energy = EXPLOSION_ENERGY
            while energy >= 0:
                wall = self.map.get_wall(pos)
                hits.append(pos)
                pos += step

                if wall == WALL_HARD:
                    hits.pop()
                    break
                elif wall == WALL_SOFT:
                    energy -= 4
                else:
                    energy -= 2
        return hits

    def update(self):
        self._update_players()
        self._update_items()
        self._update_round()

    def _update_players(self):
        fires = filter(lambda i: i.type == "fire", self.items.copy().values())
        players = self.players.values()

        for player in players:
            if player.is_dead():
                continue

            # update fire
            for fire in fires:
                if player.pos == fire.pos:
                    player.health -= 1

            # update health
            if player.is_dead():
                self.add_item("boots", player.pos, player, ttl=1e6)
                player.pos = Vec(-1, -1)

            # update movement
            if player.pos != player.target_pos:

                # calculate where to step
                step = (player.target_pos - player.pos).clamp(-1, 1, -1, 1)
                new_pos = (player.pos + step).clamp(
                    0, self.map.width, 0, self.map.height
                )

                # check wall at new pos
                if self.map.get_wall(new_pos):
                    # TODO change the targety x to player x
                    player.target_pos = player.pos
                else:
                    player.pos = new_pos

    def _update_items(self):
        old_items = self.items.copy().items()
        for id, item in old_items:
            item.update()

            if item.is_dead():
                del self.items[id]
                if item.type == "explosive":
                    self.do_explosion(item.pos)
                    if item.player is not None:
                        self.players[item.player].explosives += 1

    def _update_round(self):
        live_players = list(filter(lambda p: p.health > 0, self.players.values()))
        is_round_end = len(live_players) == 0

        if is_round_end:
            for player in self.players.values():
                player.health = PLAYER_HEALTH
                player.pos = self.map.start_pos(player.id)

            self.items = {}
            self.map = Map.default()

            print("round restarted", file=stderr)
