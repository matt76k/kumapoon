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

    def _setup(self):
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(CONST.WIDTH, CONST.HEIGHT)
        self.gui_camera = arcade.Camera(CONST.WIDTH, CONST.HEIGHT)
        self.map = MapLoader("assets/data/map.json")
        self.scene.add_sprite('Flag', self.map.flag)

        self.player = Player()
        self.player.center_x = CONST.WIDTH // 2
        self.player.center_y = 100
        self.scene.add_sprite('Player', self.player)

        self.key_state = (False, False, False)
        for level in self.map.levels:
            self.obstacle_list.extend(level.obstacles)
        self.scene.add_sprite_list('Blocks', sprite_list=self.obstacle_list)

        arcade.set_background_color(self.map.levels[self.current_level].bg)

        gravity = (0, -CONST.GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=CONST.DAMPING, gravity=gravity)
        self.physics_engine.add_sprite(
            self.player, friction=PLAYER.FRICTION, mass=PLAYER.MASS,
            moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type="player",
            max_horizontal_velocity=PLAYER.MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=PLAYER.MAX_VERTICAL_SPEED
        )
        self.physics_engine.add_sprite_list(
            self.scene.get_sprite_list('Blocks'), friction=CONST.WALL_FRICTION,
            collision_type="wall", body_type=arcade.PymunkPhysicsEngine.STATIC
        )

        def _block_hit_hundler(player_sprite, block_sprite, _arbiter, _space, _data):
            if abs(_arbiter.normal[0]) > 0.8:
                print(_arbiter.normal)
                impulse_x, impulse_y = _arbiter.total_impulse
                normal_x, normal_y = _arbiter.normal
                self.physics_engine.apply_impulse(
                    self.player, (impulse_x * abs(normal_x), impulse_y * abs(normal_y))
                )
                print('bounce_side', _arbiter.total_impulse)

            if _arbiter.normal[1] > 0 and _arbiter.total_impulse[1] < 0:
                f_x, f_y = _arbiter.total_impulse
                self.physics_engine.apply_impulse(self.player, (-f_x * 0.6, f_y * 0.6))
                print('bounce_down', _arbiter.total_impulse)

        self.physics_engine.add_collision_handler(
            'player', 'wall', post_handler=_block_hit_hundler
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
            exit(0)

        self.key_state = self.controller.update(
            self.player, current=self.key_state, key=key, pressed=True
        )
        if key == arcade.key.SPACE:
            self.released = False

    def on_key_release(self, key, modifiers):
        self.key_state = self.controller.update(
            self.player, current=self.key_state, key=key, pressed=False
        )
        if key == arcade.key.SPACE:
            self.released = True

    def update_player(self):
        left, right, jump = self.key_state
        self.player.isLeftPressed = left
        self.player.isRightPressed = right
        self.player.isJumpPressed = jump

        is_on_ground = self.physics_engine.is_on_ground(self.player)
        force = (0, 0)

        if left and not right:
            force = (-PLAYER.RUN_SPEED, 0)
            self.physics_engine.set_friction(self.player, 0)
        elif right and not left:
            force = (PLAYER.RUN_SPEED, 0)
            self.physics_engine.set_friction(self.player, 0)
        elif (not left) and (not right):
            self.physics_engine.set_friction(self.player, 1.0)

        if is_on_ground and not jump:
            self.physics_engine.apply_force(self.player, force)
        else:
            self.physics_engine.set_friction(self.player, 1.0)

        if jump and is_on_ground:
            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.player.update_jumptimer()
        elif self.released and is_on_ground:
            jump_timer = min(self.player.jump_timer, PLAYER.MAX_JUMP_TIMER)
            force_y = 1000 + jump_timer * 30
            self.physics_engine.apply_impulse(self.player, (force[0], force_y))
            self.released = False
            self.player.jump_timer = 0

        self._edge_bounce()

    def _edge_bounce(self):
        player_object = self.physics_engine.get_physics_object(self.player)
        velocity_x = player_object.body.velocity[0]
        if self.player.right > CONST.WIDTH and velocity_x > 0:
            self.physics_engine.set_horizontal_velocity(self.player, -velocity_x)
        elif self.player.left < 0 and velocity_x < 0:
            self.physics_engine.set_horizontal_velocity(self.player, -velocity_x)

    def _switch_camera(self):
        if self.player.center_y > CONST.HEIGHT * (self.current_level + 1):
            if self.map.is_top(self.current_level):
                return
            self.current_level += 1
            self.camera.move_to((0, CONST.HEIGHT * self.current_level))

        elif self.player.center_y < CONST.HEIGHT * self.current_level:
            self.current_level -= 1
            self.camera.move_to((0, CONST.HEIGHT * self.current_level))

    def on_update(self, delta_time):
        self.update_player()
        self.physics_engine.step()

    def _check_clear(self):
        collide_flag = arcade.check_for_collision(
            self.player, self.map.flag
        )
        if collide_flag:
            self.cleared = True

    def _draw_jump_timer(self):
        power = int(255 * (self.player.jump_timer / PLAYER.MAX_JUMP_TIMER))
        arcade.draw_circle_filled(
            self.player.center_x, self.player.center_y,
            30 * (self.player.jump_timer / PLAYER.MAX_JUMP_TIMER) + 20,
            (power, 255 - power, 0)
        )

    def _draw_debug_text(self):
        arcade.draw_text(
            f"level: {self.current_level}", 10, CONST.HEIGHT - 30, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"({self.player.center_x:.1f}, {self.player.center_y:.1f})",
            10, CONST.HEIGHT - 50, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"on_ground: {self.physics_engine.is_on_ground(self.player)}",
            10, CONST.HEIGHT - 70, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"jump_timer: {self.player.jump_timer}",
            10, CONST.HEIGHT - 90, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"{self.physics_engine.get_physics_object(self.player).body.velocity}",
            10, CONST.HEIGHT - 110, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"{self.player.left:.1f}, {self.player.right:.1f}",
            10, CONST.HEIGHT - 130, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            f"{self.physics_engine.get_physics_object(self.player).shape.friction}",
            10, CONST.HEIGHT - 150, arcade.color.BLACK, 20
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self._switch_camera()
        self._draw_jump_timer()
        self.scene.draw()
        # self.player.draw_hit_box()
        # self.obstacle_list.draw_hit_boxes()
        self.gui_camera.use()
        # self._draw_debug_text()


if __name__ == "__main__":
    game = Game(Human())
    game._setup()
    arcade.run()
