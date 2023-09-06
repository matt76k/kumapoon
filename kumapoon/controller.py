from abc import ABC, abstractmethod
from typing import Tuple

import arcade
import random

from .player import Player


class Controller(ABC):
    @abstractmethod
    def update(self, player: Player,
               obstacles: arcade.SpriteList, **kwargs) -> Tuple[bool, bool, bool]:
        return True, True, True


class RandomPlayer(Controller):
    def __init__(self) -> None:
        super().__init__()

    def update(self, player: Player,
               obstacles: arcade.SpriteList, **kwargs) -> tuple[bool, bool, bool]:
        return tuple(random.choice([True, False]) for _ in range(3))


class Human(Controller):
    def __init__(self) -> None:
        super().__init__()

    def update(self, player: Player,
               obstacles: arcade.SpriteList, **kwargs) -> Tuple[bool, bool, bool]:

        keys = list(kwargs['current'])
        if kwargs['key'] == arcade.key.LEFT:
            key_index = 0
            print('left')
        elif kwargs['key'] == arcade.key.RIGHT:
            key_index = 1
            print('right')
        elif kwargs['key'] == arcade.key.SPACE:
            key_index = 2
            print('space')
        keys[key_index] = kwargs['pressed']

        return tuple(keys)
        # pressed_keys = arcade.get_input().keyboard
        # return pressed_keys[arcade.Key.LEFT], pressed_keys[arcade.Key.RIGHT], pressed_keys[arcade.Keyey.SPACE]
