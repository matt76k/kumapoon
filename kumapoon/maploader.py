import random

import arcade
import yaml
from pydantic import BaseModel, ConfigDict

from .shapes import Block
from .constants import Constants as CONST


class Level(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    bg: tuple[int, int, int]
    obstacles: list[arcade.Sprite]


class MapLoader:
    def __init__(self, path):
        self.levels = []
        self._load_map(path)

    def is_top(self, level: int) -> bool:
        return len(self.levels) - 1 == level

    def _load_map(self, path):
        with open(path, "r") as f:
            map = yaml.safe_load(f)
        self.levels += [Level(bg=(135, 206, 235), obstacles=[]) for _ in range(len(map))]
        for idx, level in map.items():
            for block in level["blocks"]:
                self.levels[idx].obstacles.append(Block(*block))

    def add_level(self, current_level=0):
        num_blocks = random.randint(3, 8)
        level = Level(bg=(135, 206, 235), obstacles=[])
        for _ in range(num_blocks):
            x = random.randint(0, CONST.WIDTH)
            _y = CONST.HEIGHT * current_level
            y = random.randint(_y, _y + CONST.HEIGHT)
            width = random.randint(30, 150)
            height = random.randint(20, 50)

            level.obstacles.append(Block(x, y, width, height))
        self.levels.append(level)
