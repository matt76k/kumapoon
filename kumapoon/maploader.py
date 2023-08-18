from typing import List, Tuple

import pygame
import yaml
from pydantic import BaseModel, ConfigDict

from .shapes import Block


class Level(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    bg: Tuple[int, int, int]
    obstacles: List[pygame.sprite.Sprite]


class MapLoader:
    def __init__(self, path):
        self.path = path
        with open(path, "r") as f:
            self.data = yaml.safe_load(f)

    def loadLevels(self):
        levels = [Level(bg=(135, 206, 235), obstacles=[]) for _ in range(len(self.data))]
        for idx, data in self.data.items():
            for block in data["blocks"]:
                levels[idx].obstacles.append(Block(*block))

        return levels
