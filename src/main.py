import arcade

from kumapoon.constants import Constants as CONST
from kumapoon.constants import PlayerConstants as PLAYER
from kumapoon.controller import Controller, Human, RandomPlayer
from kumapoon.maploader import MapLoader
from kumapoon.player import Player


class Game(arcade.Window):
    def __init__(self, controller: Controller):
        super().__init__(CONST.WIDTH, CONST.HEIGHT, "Kumapoon")

        self.controller = controller
        self.scene: arcade.Scene | None = None
        self.player: arcade.Sprite | None = None
        self.obstacle_list: arcade.SpriteList | None = arcade.SpriteList()
        self.current_level = 0

        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.space_pressed: bool = False

        self.released: bool = False

        self.physics_engine: arcade.PymunkPhysicsEngine | None = None
        self.camera = None
        self.gui_camera = None

    def setup(self):
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(CONST.WIDTH, CONST.HEIGHT)
        self.gui_camera = arcade.Camera(CONST.WIDTH, CONST.HEIGHT)
        self.map = MapLoader("assets/data/map.yaml")

        self.player = Player()
        self.player.center_x = CONST.WIDTH // 2
        self.player.center_y = 100
        self.scene.add_sprite('Player', self.player)

        self.key_state = (False, False, False)
        self.obstacle_list.extend(self.map.levels[0].obstacles)
        self.scene.add_sprite_list('Blocks', sprite_list=self.obstacle_list)

        arcade.set_background_color(self.map.levels[self.current_level].bg)

        gravity = (0, -CONST.GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=CONST.DAMPING, gravity=gravity)
        self.physics_engine.add_sprite(self.player,
                                       friction=PLAYER.FRICTION,
                                       mass=PLAYER.MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER.MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER.MAX_VERTICAL_SPEED)
        self.physics_engine.add_sprite_list(self.scene.get_sprite_list('Blocks'),
                                            friction=CONST.WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        def block_hit_hundler(player_sprite, block_sprite, _arbiter, _space, _data):
            # if self.physics_engine.is_on_ground(self.player):
            #     return

            if _arbiter.normal[0] != 0:
                velocity_x = _arbiter.total_impulse[0] * 0.5
                self.physics_engine.set_horizontal_velocity(self.player, velocity_x)
            # print(_arbiter.normal)

        self.physics_engine.add_collision_handler('player', 'wall', post_handler=block_hit_hundler)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
            exit(0)

        self.key_state = self.controller.update(self.player,
                                                current=self.key_state,
                                                key=key, pressed=True)
        if key == arcade.key.SPACE:
            self.released = False

    def on_key_release(self, key, modifiers):
        self.key_state = self.controller.update(self.player,
                                                current=self.key_state,
                                                key=key, pressed=False)
        if key == arcade.key.SPACE:
            self.released = True

    def update_player(self):
        left, right, jump = self.key_state
        self.player.isLeftPressed = left
        self.player.isRightPressed = right
        self.player.isJumpPressed = jump

        is_on_ground = self.physics_engine.is_on_ground(self.player)
        force_x = force_y = 0

        if left and not right:
            force_x = -PLAYER.RUN_SPEED
        elif right and not left:
            force_x = PLAYER.RUN_SPEED

        if is_on_ground and not jump:
            self.physics_engine.set_horizontal_velocity(self.player, force_x)

        if jump and is_on_ground:
            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.player.update_jumptimer()
            power = int(255 * (self.player.jump_timer / PLAYER.MAX_JUMP_TIMER))
            arcade.draw_circle_filled(
                self.player.center_x, self.player.center_y,
                30 * (self.player.jump_timer / PLAYER.MAX_JUMP_TIMER) + 20,
                (power, 255 - power, 0)
            )
        elif self.released:
            jump_timer = min(self.player.jump_timer, PLAYER.MAX_JUMP_TIMER)
            force_y = 1000 + jump_timer * 30
            self.physics_engine.apply_impulse(self.player, (force_x, force_y))
            self.released = False
            self.player.jump_timer = 0

        self.edge_bounce()

    def edge_bounce(self):
        player_object = self.physics_engine.get_physics_object(self.player)
        velocity_x = player_object.body.velocity[0]
        if self.player.right > CONST.WIDTH and velocity_x > 0:
            self.physics_engine.set_horizontal_velocity(self.player, -velocity_x)
        elif self.player.left < 0 and velocity_x < 0:
            self.physics_engine.set_horizontal_velocity(self.player, -velocity_x)

    def draw_debug_text(self):
        arcade.draw_text(f"level: {self.current_level}",
                         10, CONST.HEIGHT - 30, arcade.color.BLACK, 20)
        arcade.draw_text(f"({self.player.center_x:.1f}, {self.player.center_y:.1f})",
                         10, CONST.HEIGHT - 50, arcade.color.BLACK, 20)
        arcade.draw_text(f"on_ground: {self.physics_engine.is_on_ground(self.player)}",
                         10, CONST.HEIGHT - 70, arcade.color.BLACK, 20)
        arcade.draw_text(f"jump_timer: {self.player.jump_timer}",
                         10, CONST.HEIGHT - 90, arcade.color.BLACK, 20)
        arcade.draw_text(f"{self.physics_engine.get_physics_object(self.player).body.velocity}",
                         10, CONST.HEIGHT - 110, arcade.color.BLACK, 20)
        arcade.draw_text(f"{self.player.left:.1f}, {self.player.right:.1f}",
                         10, CONST.HEIGHT - 130, arcade.color.BLACK, 20)

    def switch_camera(self):
        if self.player.top > CONST.HEIGHT * (self.current_level + 1):
            self.current_level += 1
            self.obstacle_list.clear()
            self.obstacle_list.extend(self.map.levels[self.current_level].obstacles)
            self.camera.move_to((0, CONST.HEIGHT * self.current_level))

        elif self.player.bottom < CONST.HEIGHT * self.current_level:
            self.current_level -= 1
            self.obstacle_list.clear()
            self.obstacle_list.extend(self.map.levels[self.current_level].obstacles)
            self.camera.move_to((0, CONST.HEIGHT * self.current_level))

    def on_update(self, delta_time):
        self.update_player()
        # self.physics_engine.set_friction(self.player, 1.0)
        self.physics_engine.step()

    def on_draw(self):
        self.clear()
        self.camera.use()
        if self.map.is_top(self.current_level):
            self.map.add_level(self.current_level + 1)
            new_blocks = self.map.levels[self.current_level + 1].obstacles
            self.physics_engine.add_sprite_list(new_blocks,
                                                friction=CONST.WALL_FRICTION,
                                                collision_type="wall",
                                                body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.switch_camera()
        self.scene.draw()

        self.gui_camera.use()
        self.draw_debug_text()


if __name__ == "__main__":
    game = Game(Human())
    game.setup()
    arcade.run()
