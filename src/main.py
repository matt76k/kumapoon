import pygame

from kumapoon.maploader import MapLoader
from kumapoon.constants import *
from kumapoon.player import Player

pygame.init()
pygame.display.set_caption("Kumapoon")

class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.fps = pygame.time.Clock().tick
        self.player = Player()
        self.levels = MapLoader("assets/data/map.yaml").loadLevels()
        self.current_level = 0
    
    def check_event(self, event):
        for e in pygame.event.get():
            if e.type == event:
                return True
        return False
    
    def update_player(self, obstacles):
        pressedKeys = pygame.key.get_pressed()
        self.player.isLeftPressed = pressedKeys[pygame.K_LEFT]
        self.player.isRightPressed = pressedKeys[pygame.K_RIGHT]
        self.player.isJumpPressed = pressedKeys[pygame.K_SPACE]
        self.player.update(obstacles)
        self.player.draw(self.window)

    
    def run(self):
        while True:
            if self.check_event(pygame.QUIT): break

            self.window.fill(self.levels[self.current_level].bg)
            
            # current_levelが変わったら更新するように
            obstacles = pygame.sprite.Group()
            obstacles.add(*self.levels[self.current_level].obstacles)

            self.update_player(obstacles)

            obstacles.draw(self.window)
            pygame.display.update()
            self.fps(FPS)

Game().run()