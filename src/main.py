import random
from typing import Tuple

import pygame

from kumapoon.constants import FPS, HEIGHT, WIDTH
from kumapoon.controller import Controller, Human
from kumapoon.maploader import MapLoader
from kumapoon.player import Player


class RandomPlayer(Controller):
    def __init__(self) -> None:
        super().__init__()

    def update(self, player: Player, obstacles: pygame.sprite.Group) -> Tuple[bool, bool, bool]:
        return tuple(random.choice([True, False]) for _ in range(3))


pygame.init()
pygame.display.set_caption("Kumapoon")


class Game:
    def __init__(self, controller: Controller):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.fps = pygame.time.Clock().tick
        self.player = Player()
        self.controller = controller
        self.map = MapLoader("assets/data/map.yaml")
        self.current_level = 0

    def check_event(self, event):
        for e in pygame.event.get():
            if e.type == event:
                return True
        return False

    def update_player(self, obstacles):
        left, right, jump = self.controller.update(self.player, obstacles)
        self.player.isLeftPressed = left
        self.player.isRightPressed = right
        self.player.isJumpPressed = jump
        self.player.update(obstacles)
        self.player.draw(self.window)

    def run(self):
        obstacles = pygame.sprite.Group()
        obstacles.add(*self.map.levels[self.current_level].obstacles)

        while True:
            if self.check_event(pygame.QUIT):
                break

            if self.map.is_top(self.current_level):
                self.map.add_level()

            if self.player.rect.top < 0:
                self.current_level += 1
                obstacles.empty()
                obstacles.add(*self.map.levels[self.current_level].obstacles)
                self.player.rect.top += HEIGHT
            elif self.player.rect.bottom > HEIGHT:
                self.current_level -= 1
                obstacles.empty()
                obstacles.add(*self.map.levels[self.current_level].obstacles)
                self.player.rect.top -= HEIGHT

            self.window.fill(self.map.levels[self.current_level].bg)
            self.update_player(obstacles)
            obstacles.draw(self.window)
            pygame.display.update()
            self.fps(FPS)


# 人間でプレイしたいとき
Game(Human()).run()
# AIでやる場合
# Game(RandomPlayer()).run()
