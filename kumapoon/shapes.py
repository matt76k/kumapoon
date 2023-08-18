import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width=100, height=5, color=(255, 255, 255)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y