import os
import random

import arcade

# Корень проекта (родитель папки code/) — пути к ресурсам работают при любом cwd
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RES = os.path.join(_PROJECT_ROOT, "res")

GHOST_ANIMATION_SPEED = 0.5
HERO_ANIMATION_SPEED = 0.25

GHOST_SPEED = 100
SPIDER_SPEED = 75


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.change_timer = 0

    def update(self, delta_time: float, player_x, player_y, speed):
        '''if self.center_x < player_x: ПЕРВЫЙ ВАРИАНТ ДВИЖЕНИЯ
            self.change_x = speed
        elif self.center_x > player_x:
            self.change_x = -speed
        if self.center_y < player_y:
            self.change_y = speed
        elif self.center_y > player_y:
            self.change_y = -speed'''
        self.change_timer += delta_time
        if self.change_timer >= 2:
            self.change_y = random.choice([speed, -speed, 0])
            self.change_x = random.choice([speed, -speed, 0])
            self.change_timer = 0
        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time


class Spider(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.up_image = arcade.load_texture(os.path.join(_RES, "spider_animation", "up.png"))
        self.down_image = arcade.load_texture(os.path.join(_RES, "spider_animation", "down.png"))
        self.left_image = arcade.load_texture(os.path.join(_RES, "spider_animation", "left.png"))
        self.right_image = arcade.load_texture(os.path.join(_RES, "spider_animation", "right.png"))
        self.texture = self.up_image
        self.speed = SPIDER_SPEED

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
    def __init__(self, x, y):
        super().__init__(x, y)
        self.scale = 2
        self.textures = [
            arcade.load_texture(os.path.join(_RES, "ghost_animation", "1.png")),
            arcade.load_texture(os.path.join(_RES, "ghost_animation", "2.png")),
        ]
        self.texture = self.textures[0]
        self.frame = 0
        self.animation_timer = 0
        self.speed = GHOST_SPEED

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
        self.scale = 1.75
        self.center_x = x
        self.center_y = y
        hero_res = os.path.join(_RES, "hero_animation")
        self.idle_texture = arcade.load_texture(os.path.join(hero_res, "default.png"))
        self.walk_up_textures = []
        self.walk_down_textures = []
        self.walk_left_textures = []
        self.walk_right_textures = []
        for i in range(4):
            self.walk_up_textures.append(arcade.load_texture(os.path.join(hero_res, f"up{i}.png")))
            self.walk_down_textures.append(arcade.load_texture(os.path.join(hero_res, f"down{i}.png")))
            self.walk_left_textures.append(arcade.load_texture(os.path.join(hero_res, f"left{i}.png")))
            self.walk_right_textures.append(arcade.load_texture(os.path.join(hero_res, f"right{i}.png")))
        self.frame = 0
        self.animation_timer = 0
        self.direction = 0
        """направления анимации: 1 - вверх, 2 - вправо, 3 - вниз, 4 - влево, 0 - не идет"""
        self.texture = self.idle_texture

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
        self.direction = new_direction
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


class Bullet(arcade.Sprite):
    def __init__(self, speedx, speedy, x, y, enemies, size):
        super().__init__(
            arcade.SpriteSolidColor(16, 16, color=arcade.color.WHITE).texture
        )
        self.center_x = x
        self.center_y = y
        self.enemies = enemies
        self.speedx = speedx
        self.speedy = speedy
        self.size_window = size



