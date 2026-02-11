import random
import sys
import time
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
MAP_SIZE = int(25 * 16 * TILE_SCALE)
HERO_START_X = MAP_SIZE - 16 * TILE_SCALE * 8
HERO_START_Y = MAP_SIZE - 16 * TILE_SCALE * 5

# Камера
CAMERA_LERP = 0.12

# Урон
SPIDER_DAMAGE = 10
GHOST_DAMAGE = 20
BULLET_SPEED = 300
COOLDOWN = 0.5

from code.database import init_db, save_run
from code.statistics_view import StatisticsView


def gravity_drag(p):  # Для искр: чуть вниз и затухание скорости
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def make_ring(x, y, count=40, radius=32.0):
    # Кольцо искр (векторы направлены по окружности)
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_on_circle((0.0, 0.0), radius),
            lifetime=random.uniform(0.8, 1.4),
            start_alpha=255, end_alpha=0,
            scale=random.uniform(1.2, 2),
            mutation_callback=gravity_drag,
        ),
    )


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.option_start = None
        self.option_statistics = None
        self.option_exit = None
        self._text_title = None
        self._text_start = None
        self._text_statistics = None
        self._text_exit = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self._setup_button_areas()
        self._create_text_objects()

    def _setup_button_areas(self):
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        self.option_start = (cx - 120, cy + 32, 240, 44)
        self.option_statistics = (cx - 120, cy - 28, 240, 44)
        self.option_exit = (cx - 120, cy - 88, 240, 44)

    def _create_text_objects(self):
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        self._text_title = arcade.Text(
            TITLE, cx, SCREEN_HEIGHT - 120,
            arcade.color.WHEAT, 48,
            anchor_x="center", anchor_y="center",
            font_name=("arial", "calibri"),
        )
        self._text_start = arcade.Text(
            "Начать игру", cx, cy + 54,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
        )
        self._text_statistics = arcade.Text(
            "Статистика", cx, cy - 6,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
        )
        self._text_exit = arcade.Text(
            "Выйти", cx, cy - 66,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        arcade.draw_lbwh_rectangle_filled(cx - 120, cy + 32, 240, 44, arcade.color.DIM_GRAY)
        arcade.draw_lbwh_rectangle_filled(cx - 120, cy - 28, 240, 44, arcade.color.DIM_GRAY)
        arcade.draw_lbwh_rectangle_filled(cx - 120, cy - 88, 240, 44, arcade.color.DIM_GRAY)
        self._text_title.draw()
        self._text_start.draw()
        self._text_statistics.draw()
        self._text_exit.draw()

    def _is_inside(self, x, y, rect):
        rx, ry, w, h = rect
        return rx <= x <= rx + w and ry <= y <= ry + h

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self._is_inside(x, y, self.option_start):
            self.window.show_view(GameView())
        elif self._is_inside(x, y, self.option_statistics):
            self.window.show_view(StatisticsView(MenuView()))
        elif self._is_inside(x, y, self.option_exit):
            self.window.close()


class PauseView(arcade.View):
    def __init__(self, game_view: "GameView"):
        super().__init__()
        self.game_view = game_view
        self._text_title = None
        self._text_hint = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        if self.game_view._music_player is not None:
            arcade.stop_sound(self.game_view._music_player)
            self.game_view._music_player = None
        cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        self._text_title = arcade.Text(
            "Пауза",
            cx, cy + 30,
            arcade.color.WHITE, 48,
            anchor_x="center", anchor_y="center",
            font_name=("arial", "calibri"),
        )
        self._text_hint = arcade.Text(
            "Esc — продолжить",
            cx, cy - 40,
            arcade.color.LIGHT_GRAY, 22,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 180),
        )
        self._text_title.draw()
        self._text_hint.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.hero = None
        self._text_hint = None
        self.bullet_list = None
        self.win_ring = None
        self.current_map_num = None  # 1, 2 или 3 — текущая карта
        self.world_camera = None
        self.gui_camera = None
        self.victory_triggered = False  # победа уже показана на этой карте
        self.game_over_triggered = False  # проигрыш уже обработан (HP <= 0)
        self.transition_timer = None  # таймер до перехода на след карту
        self.victory_title_text = None
        self.victory_timer_text = None
        self._game_music = None
        self._music_player = None
        self.total_enemies_killed = 0
        self.total_bullets_fired = 0
        self.start_time = None
        self.level_text = None

    def _load_map(self, map_num: int):
        self.current_map_num = map_num
        self.win_ring = None
        self.victory_triggered = False
        self.transition_timer = None
        self.victory_title_text = None
        self.victory_timer_text = None

        map_path = str(MAPS_DIR / f"map{map_num}.tmx")
        self.tile_map = arcade.load_tilemap(map_path, scaling=TILE_SCALE)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # обязательно чтоб игрок поверх карты был
        # по центру располагаю героя (upd: пока попробую сверху справа)
        start_x = HERO_START_X
        start_y = HERO_START_Y
        self.hero = Hero(start_x, start_y)
        self.scene.add_sprite_list("player")
        self.scene["player"].append(self.hero)

        self.enemies = 10
        self.scene.add_sprite_list("enemies")
        self.scene.add_sprite_list("bullets")
        for i in range(self.enemies // 2):
            self.scene["enemies"].append(Ghost(random.randint(0, MAP_SIZE),
                                               random.randint(0, MAP_SIZE)))
        for i in range(self.enemies // 2):
            self.scene["enemies"].append(Spider(random.randint(0, MAP_SIZE),
                                                random.randint(0, MAP_SIZE)))
        # выигрыши проигрыши и тд
        self.hp = 100
        self.damage_timer = 0
        self.cooldown_timer = 0
        self.bullet_list = arcade.SpriteList()

        self._text_hint = arcade.Text(
            "WASD — движение, Esc — меню",
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5,
            arcade.color.LIGHT_GRAY, 14,
            anchor_x="left", anchor_y="top",
        )
        self.score_text = arcade.Text(
            f"Врагов осталось: {self.enemies}",
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5,
            arcade.color.RED, 20,
            anchor_x="left", anchor_y="top",
        )
        self.hp_text = arcade.Text(
            f"HP: {self.hp}",
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5 - 28,
            arcade.color.GREEN, 20,
            anchor_x="left", anchor_y="top",
        )
        self.level_text = arcade.Text(
            f"Уровень {map_num}",
            MAP_SIZE - TILE_SCALE * 16 * 10, MAP_SIZE - TILE_SCALE * 16 * 0.5 + 28,
            arcade.color.LIGHT_GRAY, 18,
            anchor_x="left", anchor_y="top",
        )
        # камера, движок
        self.engine = arcade.PhysicsEngineSimple(
            player_sprite=self.hero,
            walls=(self.scene["material"],)
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        if self._game_music is None:
            self._game_music = arcade.load_sound("res/soundtrack.mp3")
        self._music_player = arcade.play_sound(self._game_music, loop=True)

        if self.world_camera is None:
            self.world_camera = arcade.Camera2D()
            self.gui_camera = arcade.Camera2D()

        # первый заход — всегда уровень 1; далее 2 и 3; после 3 — экран победы
        if self.current_map_num is None:
            self.start_time = time.time()
            self._load_map(1)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self._text_hint.draw()
        if self.level_text is not None:
            self.level_text.draw()
        self.score_text.draw()
        self.hp_text.draw()
        self.gui_camera.use()
        self.world_camera.use()
        if self.win_ring is not None:
            self.win_ring.draw()
        if self.victory_title_text is not None and self.victory_timer_text is not None:
            self.victory_title_text.draw()
            self.victory_timer_text.draw()

    def on_update(self, delta_time: float):
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
        if self.hp <= 0 and not self.game_over_triggered:
            self.game_over_triggered = True
            run_time = time.time() - self.start_time
            save_run(run_time, self.total_bullets_fired, self.total_enemies_killed, won=False)
            # переключаем вид на следующем кадре, чтобы клики не терялись
            arcade.schedule_once(lambda dt: self.lose(), 0)
            return
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
                self.total_enemies_killed += 1
                continue
            bullet.center_x += bullet.speedx * delta_time
            bullet.center_y += bullet.speedy * delta_time
            if min(bullet.center_x, bullet.center_y) <= 0 \
                    or max(bullet.center_x, bullet.center_y) >= bullet.size_window:
                bullet.kill()
        self.score_text.text = f"Врагов осталось: {self.enemies}"
        self.score_text.x, self.score_text.y = self.world_camera.position
        self.score_text.y += SCREEN_HEIGHT // 2
        self.score_text.x -= SCREEN_WIDTH // 2
        self.hp_text.text = f"HP: {self.hp}"
        self.hp_text.x = self.score_text.x
        self.hp_text.y = self.score_text.y - 28
        if self.level_text is not None:
            self.level_text.x = self.score_text.x
            self.level_text.y = self.score_text.y + 28
        if self.enemies <= 0:
            if not self.victory_triggered:
                self.victory_triggered = True  # чтобы один раз только
                self.win()
                self.transition_timer = 5.0
            if self.transition_timer is not None:
                self.transition_timer -= delta_time
                if self.victory_timer_text is not None:
                    sec_left = round(self.transition_timer)
                    self.victory_timer_text.text = f"Следующая карта через {sec_left} сек"
                if self.transition_timer <= 0:
                    self.transition_timer = None
                    if self.current_map_num == 3:
                        run_time = time.time() - self.start_time
                        save_run(run_time, self.total_bullets_fired, self.total_enemies_killed, won=True)
                        self.window.show_view(VictoryView(
                            run_time, self.total_bullets_fired, self.total_enemies_killed
                        ))
                    else:
                        self._go_next_map()

        if self.win_ring is not None:
            self.win_ring.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(PauseView(self))
            return
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = HERO_SPEED
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = -HERO_SPEED

        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = -HERO_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = HERO_SPEED

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        if self.game_over_triggered:
            return
        self.total_bullets_fired += 1
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

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = 0
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = 0
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = 0

    def _go_next_map(self):
        # уровни; после 3 показывается VictoryView, сюда не заходим
        next_num = self.current_map_num + 1
        self._load_map(next_num)

    def win(self):
        self.win_ring = make_ring(self.hero.center_x, self.hero.center_y)
        cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        self.victory_title_text = arcade.Text(
            "Победа!",
            cx, cy + 50,
            arcade.color.WHITE, 36,
            anchor_x="center", anchor_y="center",
            font_name=("arial", "calibri"),
        )
        self.victory_timer_text = arcade.Text(
            "Следующая карта через 5 сек",
            cx, cy - 30,
            arcade.color.WHITE, 22,
            anchor_x="center", anchor_y="center",
        )

    def lose(self):
        self.window.show_view(GameOverView())


class GameOverView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_RED)
        cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        self._title = arcade.Text(
            "Game Over",
            cx, cy + 20,
            arcade.color.WHITE, 48,
            anchor_x="center", anchor_y="center",
        )
        self._hint = arcade.Text(
            "Enter или клик — в меню",
            cx, cy - 50,
            arcade.color.LIGHT_GRAY, 20,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        self._title.draw()
        self._hint.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_mouse_press(self, x, y, button, modifiers):
        self.window.show_view(MenuView())


class VictoryView(arcade.View):
    def __init__(self, time_seconds: float, bullets_used: int, enemies_killed: int):
        super().__init__()
        self.time_seconds = time_seconds
        self.bullets_used = bullets_used
        self.enemies_killed = enemies_killed
        self._texts = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)
        cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        mins = int(self.time_seconds // 60)
        secs = int(self.time_seconds % 60)
        time_str = f"{mins} мин {secs} сек"
        self._texts = [
            arcade.Text("Игра пройдена!", cx, cy + 80, arcade.color.GOLD, 40, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Время: {time_str}", cx, cy + 30, arcade.color.WHITE, 24, anchor_x="center",
                        anchor_y="center"),
            arcade.Text(f"Пуль израсходовано: {self.bullets_used}", cx, cy - 20, arcade.color.WHITE, 24,
                        anchor_x="center", anchor_y="center"),
            arcade.Text(f"Врагов побеждено: {self.enemies_killed}", cx, cy - 70, arcade.color.WHITE, 24,
                        anchor_x="center", anchor_y="center"),
            arcade.Text("Enter или клик — в меню", cx, cy - 130, arcade.color.LIGHT_GRAY, 18, anchor_x="center",
                        anchor_y="center"),
        ]

    def on_draw(self):
        self.clear()
        for t in self._texts:
            t.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_mouse_press(self, x, y, button, modifiers):
        self.window.show_view(MenuView())


def main():
    init_db()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
