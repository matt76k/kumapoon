from typing import List
import pygame
from .constants import *

class Line:
    pass

class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/images/kumapon.png').convert_alpha()
        self.rect = self.image.get_rect()

        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.vx = 0
        self.vy = 0

        self.jump_timer = 0

        self.isOnGround = False
        self.isLeftPressed = False
        self.isRightPressed = False
        self.isJumpPressed = False

    def add_gravity(self):
        if self.isOnGround:
            self.vy = 0
            return
        
        self.vy = min(self.vy + GRAVITY, MAX_VELOCITY)

    def running(self):
        if self.isOnGround:
            if self.isJumpPressed:
                self.vx = 0
                self.vy = 0
            else:
                if self.isRightPressed:
                    self.vx = RUN_SPEED
                    self.vy = 0
                elif self.isLeftPressed:
                    self.vx = -RUN_SPEED
                    self.vy = 0                    
                else:
                    self.vx = 0
                    self.vy = 0

    def check_collisions(self, obstacles):
        hits = [hit for hit in pygame.sprite.spritecollide(self, obstacles, False)]
        if len(hits) == 0: return

        hit = hits[0]

        if self.is_moving_down():
            self.vx, self.vy = 0, 0
            self.isOnGround = True
            self.rect.bottom = hit.rect.top
        elif self.is_moving_up():
            self.vy = -self.vy
            self.isOnGround = False
            self.rect.top = hit.rect.bottom

    def jump(self):
        if self.isOnGround and self.jump_timer > 0 and not self.isJumpPressed:
            self.vy = -10 - self.jump_timer // 3
            if self.isLeftPressed:
                self.vx = -JUMP_SPEED_HORIZONTAL
            elif self.isRightPressed:
                self.vx = JUMP_SPEED_HORIZONTAL
            else:
                self.velx = 0

            self.isOnGround = False
            self.jump_timer = 0


    def update_jumptimer(self):
        if self.isOnGround and self.isJumpPressed and self.jump_timer < MAX_JUMP_TIMER:
            self.jump_timer += 1

    def update(self, obstacles):
        self.add_gravity()
        self.running()
        self.jump()
        self.isOnGround = False
        
        # 両端
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.vx = -self.vx

        self.rect.centerx += self.vx
        self.rect.centery += self.vy

        self.check_collisions(obstacles)
        self.update_jumptimer()


    def draw(self, window):
        window.blit(self.image, self.rect)

    def is_moving_down(self):
        return self.vy > 0
    
    def is_moving_up(self):
        return self.vy < 0