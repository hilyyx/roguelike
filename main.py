import random
import sys
from pathlib import Path
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount

# Корень проекта первым в path, чтобы импорт находил пакет code, а не stdlib
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import arcade
from code.sprites import *

# Константы окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Roguelike"
SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]

# Масштаб тайлов 16px в TILE_SCALE*16, стартовая карта
TILE_SCALE = 2.0
MAPS_DIR = Path(__file__).resolve().parent / "res" / "maps"
HERO_SPEED = 4
MAP_SIZE = 25 * 16 * TILE_SCALE
HERO_START_X = MAP_SIZE - 16 * TILE_SCALE * 8
HERO_START_Y = MAP_SIZE - 16 * TILE_SCALE * 5

# Камера
CAMERA_LERP = 0.12

# Урон
SPIDER_DAMAGE = 10
GHOST_DAMAGE = 20
BULLET_SPEED = 300
COOLDOWN = 0.5


def gravity_drag(p):  # Для искр: чуть вниз и затухание скорости
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def make_ring(x, y, count=40, radius=5.0):
    # Кольцо искр (векторы направлены по окружности)
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_on_circle((0.0, 0.0), radius),
            lifetime=random.uniform(0.8, 1.4),
            start_alpha=255, end_alpha=0,
            scale=random.uniform(0.4, 0.7),
            mutation_callback=gravity_drag,
        ),
    )


class EndGame(arcade.View):
    def __init__(self):
        super().__init__()


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.option_start = None  # границы кнопки Начать игру
        self.option_exit = None  # границы кнопки Выйти
        self._text_title = None
        self._text_start = None
        self._text_exit = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self._setup_button_areas()
        self._create_text_objects()

    def _setup_button_areas(self):
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        self.option_start = (cx - 120, cy - 10, 240, 44)
        self.option_exit = (cx - 120, cy - 70, 240, 44)

    def _create_text_objects(self):
        cx = SCREEN_WIDTH / 2
        self._text_title = arcade.Text(
            TITLE, cx, SCREEN_HEIGHT - 120,
            arcade.color.WHEAT, 48,
            anchor_x="center", anchor_y="center",
            font_name=("arial", "calibri"),
        )
        self._text_start = arcade.Text(
            "Начать игру", cx, SCREEN_HEIGHT / 2 + 12,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
        )
        self._text_exit = arcade.Text(
            "Выйти", cx, SCREEN_HEIGHT / 2 - 48,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        cx = SCREEN_WIDTH / 2
        # кнопки
        arcade.draw_lbwh_rectangle_filled(
            cx - 120, SCREEN_HEIGHT / 2 - 10, 240, 44, arcade.color.DIM_GRAY
        )
        arcade.draw_lbwh_rectangle_filled(
            cx - 120, SCREEN_HEIGHT / 2 - 70, 240, 44, arcade.color.DIM_GRAY
        )

        self._text_title.draw()
        self._text_start.draw()
        self._text_exit.draw()

    def _is_inside(self, x, y, rect):
        rx, ry, w, h = rect
        return rx <= x <= rx + w and ry <= y <= ry + h

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self._is_inside(x, y, self.option_start):
            self.window.show_view(GameView())
        elif self._is_inside(x, y, self.option_exit):
            self.window.close()


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.hero = None
        self._text_hint = None
        self.bullet_list = None
        self.win_ring = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        arcade.play_sound(arcade.load_sound("res/soundtrack.mp3"), loop=True)

        # Загрузка первой карты map1.tmx
        # Поменял на рандомную
        map_path = str(MAPS_DIR / f"map{random.choice((1, 2, 3))}.tmx")
        self.tile_map = arcade.load_tilemap(map_path, scaling=TILE_SCALE)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.player_spritelist = arcade.SpriteList()
        # обязательно чтоб игрок поверх карты был
        # по центру располагаю героя (upd: пока попробую сверху справа)
        # start_x = (self.tile_map.width * self.tile_map.tile_width * TILE_SCALE) / 2
        # start_y = (self.tile_map.height * self.tile_map.tile_height * TILE_SCALE) / 2
        start_x = HERO_START_X
        start_y = HERO_START_Y
        self.hero = Hero(start_x, start_y)
        self.player_spritelist.append(self.hero)
        self.scene.add_sprite_list("player")
        self.scene["player"].append(self.hero)

        # генерим противников
        self.enemies = 0
        self.scene.add_sprite_list("enemies")
        self.scene.add_sprite_list("bullets")
        for i in range(self.enemies // 2):
            self.scene["enemies"].append(Ghost(random.randint(0, MAP_SIZE),
                                               random.randint(0, MAP_SIZE)))
        for i in range(self.enemies // 2):
            self.scene["enemies"].append(Spider(random.randint(0, MAP_SIZE),
                                                random.randint(0, MAP_SIZE)))
        # пока подсказки, хз можно убрать
        self._text_hint = arcade.Text(
            "WASD — движение, Esc — меню",
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5,
            arcade.color.LIGHT_GRAY, 14,
            anchor_x="left", anchor_y="top",
        )
        self.score_text = arcade.Text(
            str(self.enemies),
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5,
            arcade.color.RED, 20,
            anchor_x="left", anchor_y="top",
        )
        # камера, движок
        self.engine = arcade.PhysicsEngineSimple(
            self.hero,
            walls=(self.scene["material"],)
        )
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # выигрыши проигрыши и тд
        self.hp = 100
        self.damage_timer = 0
        self.cooldown_timer = 0
        self.bullet_list = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self._text_hint.draw()
        self.score_text.draw()
        self.gui_camera.use()
        self.world_camera.use()

    def on_update(self, delta_time: float):
        # этот блок надо убрать потом
        '''self.hero.center_x += self.hero.change_x * HERO_SPEED * delta_time
        self.hero.center_y += self.hero.change_y * HERO_SPEED * delta_time
        map_w = self.tile_map.width * self.tile_map.tile_width * TILE_SCALE
        map_h = self.tile_map.height * self.tile_map.tile_height * TILE_SCALE
        margin = 20
        self.hero.center_x = max(margin, min(map_w - margin, self.hero.center_x))
        self.hero.center_y = max(margin, min(map_h - margin, self.hero.center_y))'''
        self.hero.update(delta_time)
        self.scene["enemies"].update(delta_time, self.hero.center_x, self.hero.center_y)
        self.scene["bullets"].update(delta_time)

        self.hero.left = max(self.hero.left, 0)
        self.hero.right = min(self.hero.right, MAP_SIZE)
        self.hero.bottom = max(self.hero.bottom, 0)
        self.hero.top = min(self.hero.top, HERO_START_Y + 16)
        for enemy in self.scene["enemies"]:
            enemy.left = max(enemy.left, 0)
            enemy.right = min(enemy.right, MAP_SIZE)
            enemy.bottom = max(enemy.bottom, 0)
            enemy.top = min(enemy.top, HERO_START_Y + 16)
        self.engine.update()
        # камера
        target_x = self.hero.center_x
        target_y = self.hero.center_y
        camera_x = max(SCREEN_WIDTH // 2, min(target_x, MAP_SIZE - SCREEN_WIDTH // 2))
        camera_y = max(SCREEN_HEIGHT // 2, min(target_y, MAP_SIZE - SCREEN_HEIGHT // 2))
        cx, cy = self.world_camera.position
        self.world_camera.position = (cx + (camera_x - cx) * CAMERA_LERP,
                                      cy + (camera_y - cy) * CAMERA_LERP)
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        # урон, пули и тд
        self.damage_timer += delta_time
        if self.damage_timer >= 1:
            for enemy in arcade.check_for_collision_with_list(self.hero, self.scene["enemies"]):
                if type(enemy).__name__ == "Spider":
                    self.hp -= SPIDER_DAMAGE
                else:
                    self.hp -= GHOST_DAMAGE
            self.damage_timer = 0
        if self.hp <= 0:
            self.lose()
        # пули
        self.cooldown_timer += delta_time
        for bullet in self.scene["bullets"]:
            if arcade.check_for_collision_with_list(bullet, self.scene["material"]):
                bullet.kill()
                continue
            for enemy in arcade.check_for_collision_with_list(bullet, bullet.enemies):
                enemy.kill()
                bullet.kill()
                self.enemies -= 1
                continue
            bullet.center_x += bullet.speedx * delta_time
            bullet.center_y += bullet.speedy * delta_time
            print(bullet.center_x)
            if min(bullet.center_x, bullet.center_y) <= 0 \
                    or max(bullet.center_x, bullet.center_y) >= bullet.size_window:
                bullet.kill()
        self.score_text.text = f"Врагов осталось: {self.enemies}"
        self.score_text.x, self.score_text.y = self.world_camera.position
        self.score_text.y += SCREEN_HEIGHT // 2
        self.score_text.x -= SCREEN_WIDTH // 2
        if self.enemies <= 0:
            self.win()
        if self.win_ring is not None:
            self.win_ring.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
            return
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = HERO_SPEED
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = -HERO_SPEED
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = -HERO_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = HERO_SPEED
        elif key == arcade.key.SPACE and self.cooldown_timer >= COOLDOWN:
            if self.hero.change_y != 0 or self.hero.change_x != 0:
                self.scene["bullets"].append(Bullet(
                    self.hero.change_x / HERO_SPEED * BULLET_SPEED,
                    self.hero.change_y / HERO_SPEED * BULLET_SPEED,
                    self.hero.center_x,
                    self.hero.center_y,
                    self.scene["enemies"],
                    MAP_SIZE
                ))
            else:
                self.scene["bullets"].append(Bullet(
                    0 * BULLET_SPEED,
                    -1 * BULLET_SPEED,
                    self.hero.center_x,
                    self.hero.center_y,
                    self.scene["enemies"],
                    MAP_SIZE
                ))
            self.cooldown_timer = 0
            print(len(self.scene["bullets"]))

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = 0
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = 0
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = 0

    def win(self):
        self.win_ring = make_ring(self.hero.center_x, self.hero.center_y)

    def lose(self):
        pass


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
