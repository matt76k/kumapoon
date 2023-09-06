import arcade


class Block(arcade.Sprite):
    def __init__(self, x, y, width=100, height=5, color=(255, 255, 255), gravity=1, fade=None):
        super().__init__()
        # arcade.draw_lrtb_rectangle_filled(x, x+width, y, y-height, color)
        self.image_x = x
        self.image_y = y
        self.image_width = width
        self.image_height = height
        self.center_x = x + width // 2
        self.center_y = y - height // 2
        self.gravity = gravity
        self.fade = fade
        self.texture = arcade.Texture.create_filled('block', (width, height), color)


# class Block(arcade.Sprite):
#     def __init__(self, x: float, y: float, width: float = 100, height: float = 5,
#                  color: arcade.Color = arcade.color.WHITE, gravity: float = 1,
#                  fade: float = None):
#         super().__init__()
#         center_x = x + width / 2
#         center_y = y + height / 2
#         self.image = arcade.create_rectangle(center_x, center_y, width, height, color)
#         self.gravity = gravity
#         self.fade = fade

#     def update(self):
#         # 重力で下へ移動
#         self.y += self.gravity

#         # フェードアウトする
#         if self.fade is not None:
#             self.alpha -= self.fade
#             if self.alpha <= 0:
#                 self.kill()
