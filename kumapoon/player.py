import arcade

from .constants import GRAVITY, HEIGHT, JUMP_SPEED_HORIZONTAL, MAX_JUMP_TIMER, MAX_VELOCITY, RUN_SPEED, WIDTH


class Line:
    pass


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__(filename="assets/images/kumapon.png")

        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
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

        self.vy = max(self.vy - GRAVITY, -MAX_VELOCITY)

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
        for obstacle in obstacles:
            if self.collides_with_sprite(obstacle):
                if self.is_moving_down():
                    self.vy = 0
                    self.isOnGround = True
                    self.bottom = obstacle.top
                elif self.is_moving_up():
                    self.vy = -self.vy
                    self.isOnGround = False
                    self.top = obstacle.bottom
                elif obstacle.top > self.center_y > obstacle.bottom:
                    self.vx = self.vx
                    self.isOnGround = False

    def jump(self):
        if self.isOnGround and self.jump_timer > 0 and not self.isJumpPressed:
            self.vy = 10 + self.jump_timer // 3
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
        if self.left < 0 or self.right > WIDTH:
            self.vx = -self.vx

        self.center_x += self.vx
        self.center_y += self.vy

        self.check_collisions(obstacles)
        self.update_jumptimer()

    def draw(self):
        if self.jump_timer > 0:
            power = int(255 * (self.jump_timer / MAX_JUMP_TIMER))
            arcade.draw_circle_filled(
                self.center_x, self.center_y, 30 * (self.jump_timer / MAX_JUMP_TIMER) + 20, (power, 255 - power, 0)
            )
        super().draw()
        # arcade.draw_sprite(self)

    def is_moving_down(self):
        return self.vy < 0

    def is_moving_up(self):
        return self.vy > 0

    def is_moving_left(self):
        return self.vx > 0
