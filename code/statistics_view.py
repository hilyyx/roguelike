import arcade
from code.database import get_stats


class StatisticsView(arcade.View):
    def __init__(self, back_view: arcade.View):
        super().__init__()
        self.back_view = back_view
        self._texts = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        stats = get_stats()
        w, h = self.window.width, self.window.height
        cx, cy = w / 2, h / 2

        total = stats["total_games"]
        wins = stats["wins"]
        losses = stats["losses"]
        win_rate = stats["win_rate"]
        total_bullets = stats["total_bullets"]
        record_bullets = stats["record_bullets"]
        total_kills = stats["total_kills"]

        record_str = str(record_bullets) if record_bullets is not None else "—"

        self._texts = [
            arcade.Text("Статистика", cx, cy + 180, arcade.color.WHEAT, 40, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Всего игр: {total}", cx, cy + 120, arcade.color.WHITE, 22, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Побед / Поражений: {wins} / {losses}", cx, cy + 80, arcade.color.WHITE, 22, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Винрейт: {win_rate:.1f}%", cx, cy + 40, arcade.color.GOLD, 22, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Всего пуль израсходовано: {total_bullets}", cx, cy - 10, arcade.color.WHITE, 22, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Рекорд (минимум пуль за победу): {record_str}", cx, cy - 50, arcade.color.LIGHT_GREEN, 22, anchor_x="center", anchor_y="center"),
            arcade.Text(f"Всего врагов побеждено: {total_kills}", cx, cy - 90, arcade.color.WHITE, 22, anchor_x="center", anchor_y="center"),
            arcade.Text("Enter или клик — в меню", cx, cy - 150, arcade.color.LIGHT_GRAY, 18, anchor_x="center", anchor_y="center"),
        ]

    def on_draw(self):
        self.clear()
        for t in self._texts:
            t.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.ESCAPE:
            self.window.show_view(self.back_view)

    def on_mouse_press(self, x, y, button, modifiers):
        self.window.show_view(self.back_view)
