import arcade

GHOST_ANIMATION_SPEED = 0.5
HERO_ANIMATION_SPEED = 0.25


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


class Ghost(Enemy):
    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.textures = [arcade.load_texture("../res/ghost_animation/1.png"),
                         arcade.load_texture("../res/ghost_animation/2.png")]
        self.texture = self.textures[0]
        self.frame = 0
        self.animation_timer = 0
        self.speed = speed

    def update(self, delta_time: float, player_x, player_y):
        super().update(delta_time, player_x, player_y, self.speed)
        self.animation_timer += delta_time
        if self.animation_timer >= GHOST_ANIMATION_SPEED:
            self.frame += 1
            self.frame %= 2
            self.texture = self.textures[self.frame]
            self.animation_timer = 0


class Hero(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.idle_texture = arcade.load_texture("../res/hero_animation/default.png")
        self.walk_up_textures = []
        self.walk_down_textures = []
        self.walk_left_textures = []
        self.walk_right_textures = []
        # я мог сделать одним массивом, но так проще дебажить и читать
        for i in range(4):
            self.walk_up_textures.append(
                arcade.load_texture(f"../res/hero_animation/up{i}.png")
            )
            self.walk_down_textures.append(
                arcade.load_texture(f"../res/hero_animation/down{i}.png")
            )
            self.walk_left_textures.append(
                arcade.load_texture(f"../res/hero_animation/left{i}.png")
            )
            self.walk_right_textures.append(
                arcade.load_texture(f"../res/hero_animation/right{i}.png")
            )
        self.frame = 0
        self.animation_timer = 0
        self.direction = 0
        """направления анимации: 1 - вверх, 2 - вправо, 3 - вниз, 4 - влево, 0 - не идет"""

    def update(self, delta_time):
        new_direction = None
        if self.change_x == 0 and self.change_y == 0:
            new_direction = 0
        elif self.change_y == 0 and self.change_x < 0:
            new_direction = 4
        elif self.change_y == 0 and self.change_x > 0:
            new_direction = 2
        elif self.change_y > 0:
            new_direction = 1
        elif self.change_y < 0:
            new_direction = 3
        if new_direction != self.direction:
            self.frame = 0
        self.animation_timer += delta_time
        if self.animation_timer >= HERO_ANIMATION_SPEED:
            self.frame += 1
            self.frame %= 4
            self.animation_timer = 0
            if self.direction == 0:
                self.texture = self.idle_texture
            elif self.direction == 1:
                self.texture = self.walk_up_textures[self.frame]
            elif self.direction == 2:
                self.texture = self.walk_right_textures[self.frame]
            elif self.direction == 3:
                self.texture = self.walk_down_textures[self.frame]
            elif self.direction == 4:
                self.texture = self.walk_left_textures[self.frame]
