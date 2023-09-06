import arcade

from kumapoon.constants import FPS, HEIGHT, WIDTH
from kumapoon.controller import Controller, Human, RandomPlayer
from kumapoon.maploader import MapLoader
from kumapoon.player import Player


class Game(arcade.Window):
    def __init__(self, controller: Controller):
        super().__init__(WIDTH, HEIGHT, "Kumapoon")
        self.player = Player()
        self.controller = controller
        self.map = MapLoader("assets/data/map.yaml")
        self.current_level = 0
        self.key_state = (False, False, False)
        self.obstacles = arcade.SpriteList()
        self.obstacles.extend(self.map.levels[0].obstacles)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()

        self.key_state = self.controller.update(self.player, self.obstacles,
                                                current=self.key_state, key=key, pressed=True)

    def on_key_release(self, key, modifiers):
        self.key_state = self.controller.update(self.player, self.obstacles,
                                                current=self.key_state, key=key, pressed=False)

    def update_player(self, obstacles):
        # left, right, jump = self.controller.update(self.player, self.obstacles)
        left, right, jump = self.key_state
        self.player.isLeftPressed = left
        self.player.isRightPressed = right
        self.player.isJumpPressed = jump
        self.player.update(obstacles)

    def on_draw(self):
        arcade.start_render()
        if self.map.is_top(self.current_level):
            self.map.add_level()

        arcade.draw_text(f"level: {self.current_level}",
                         10, HEIGHT - 30, arcade.color.BLACK, 20)
        arcade.draw_text(f"({self.player.center_x}, {self.player.center_y})",
                         10, HEIGHT - 50, arcade.color.BLACK, 20)

        if self.player.top > HEIGHT:
            self.current_level += 1
            self.obstacles.clear()
            self.obstacles.extend(self.map.levels[self.current_level].obstacles)
            self.player.top -= HEIGHT
        elif self.player.bottom < 0:
            self.current_level -= 1
            self.obstacles.clear()
            self.obstacles.extend(self.map.levels[self.current_level].obstacles)
            self.player.top += HEIGHT

        arcade.set_background_color(self.map.levels[self.current_level].bg)
        self.update_player(self.obstacles)
        self.player.draw()
        self.obstacles.draw()

# def main():
#     controller = Human()  # またはRandomPlayer()などの適切なコントローラーを選択
#     game = Game(controller)
#     game.run()

# if __name__ == "__main__":
#     main()


if __name__ == "__main__":
    game = Game(Human())
    game.run()
