import sys
from pathlib import Path

# Корень проекта первым в path, чтобы импорт находил пакет code, а не stdlib
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import arcade
from code.sprites import Hero

# Константы окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Roguelike"

# Масштаб тайлов 16px в TILE_SCALE*16, стартовая карта
TILE_SCALE = 2.0
MAPS_DIR = Path(__file__).resolve().parent / "res" / "maps"
HERO_SPEED = 200


class EndGame(arcade.View):
    def __init__(self):
        super().__init__()


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.option_start = None  # границы кнопки Начать игру
        self.option_exit = None   # границы кнопки Выйти
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
        #кнопки
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

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        # Загрузка первой карты map1.tmx
        map_path = str(MAPS_DIR / "map1.tmx")
        self.tile_map = arcade.load_tilemap(map_path, scaling=TILE_SCALE)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        # обязательно чтоб игрок поверх карты был
        self.scene.add_sprite_list("player")
        # по центру располагаю героя
        start_x = (self.tile_map.width * self.tile_map.tile_width * TILE_SCALE) / 2
        start_y = (self.tile_map.height * self.tile_map.tile_height * TILE_SCALE) / 2
        self.hero = Hero(start_x, start_y)
        self.scene.add_sprite("player", self.hero)
        # пока подсказки, хз можно убрать
        self._text_hint = arcade.Text(
            "WASD — движение, Esc — меню",
            10, SCREEN_HEIGHT - 24,
            arcade.color.LIGHT_GRAY, 14,
            anchor_x="left", anchor_y="top",
        )

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self._text_hint.draw()

    def on_update(self, delta_time: float):
        self.hero.center_x += self.hero.change_x * HERO_SPEED * delta_time
        self.hero.center_y += self.hero.change_y * HERO_SPEED * delta_time
        map_w = self.tile_map.width * self.tile_map.tile_width * TILE_SCALE
        map_h = self.tile_map.height * self.tile_map.tile_height * TILE_SCALE
        margin = 20
        self.hero.center_x = max(margin, min(map_w - margin, self.hero.center_x))
        self.hero.center_y = max(margin, min(map_h - margin, self.hero.center_y))
        self.hero.update(delta_time)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
            return
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = 1
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = -1
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = -1
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = 1

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.hero.change_y = 0
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.hero.change_y = 0
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.hero.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.hero.change_x = 0


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
