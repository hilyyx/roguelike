import arcade


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float, player_x, player_y, speed):
        # надо будет сюда прописать как он выбирать направление будет
        pass


class Spider(Enemy):
    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.up_image = arcade.load_texture("../res/spider_animation/up.png")
        self.down_image = arcade.load_texture("../res/spider_animation/down.png")
        self.left_image = arcade.load_texture("../res/spider_animation/left.png")
        self.right_image = arcade.load_texture("../res/spider_animation/right.png")
        self.texture = self.up_image
        self.speed = speed

    def update(self, delta_time: float, player_x, player_y):
        super().update(delta_time, player_x, player_y, self.speed)
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.up_image
        elif self.change_y == 0 and self.change_x < 0:
            self.texture = self.left_image
        elif self.change_y == 0 and self.change_x > 0:
            self.texture = self.right_image
        elif self.change_y > 0:
            self.texture = self.up_image
        elif self.change_y < 0:
            self.texture = self.down_image


class Spider(Enemy):
    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.textures = [arcade.load_texture("../res/ghost_animation/1.png"),
                         arcade.load_texture("../res/ghost_animation/2.png")]
        self.animation_speed = 0.5
        self.texture = self.textures[0]
        self.frame = 0
        self.animation_timer = 0
        self.speed = speed

    def update(self, delta_time: float, player_x, player_y):
        super().update(delta_time, player_x, player_y, self.speed)
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.frame += 1
            self.frame %= 2
            self.texture = self.textures[self.frame]
            self.animation_timer = 0
