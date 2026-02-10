"""Команды для базы данных рекордов (SQLite)."""
import sqlite3
from pathlib import Path

# Файл БД в корне проекта
DB_PATH = Path(__file__).resolve().parent.parent / "roguelike.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_seconds REAL NOT NULL,
                bullets_used INTEGER NOT NULL,
                enemies_killed INTEGER NOT NULL,
                won INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        try:
            conn.execute("ALTER TABLE runs ADD COLUMN won INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # колонка уже есть


def save_run(time_seconds: float, bullets_used: int, enemies_killed: int, won: bool = True):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO runs (time_seconds, bullets_used, enemies_killed, won) VALUES (?, ?, ?, ?)",
            (time_seconds, bullets_used, enemies_killed, 1 if won else 0),
        )


def get_stats():
    """Возвращает словарь со статистикой: total_games, wins, losses, win_rate,
    total_bullets, record_bullets (минимум пуль в победах), total_kills."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT COUNT(*) AS n, SUM(bullets_used) AS bullets, SUM(enemies_killed) AS kills, "
            "SUM(won) AS wins FROM runs"
        )
        row = cur.fetchone()
        total = row["n"] or 0
        wins = row["wins"] or 0
        losses = total - wins
        total_bullets = row["bullets"] or 0
        total_kills = row["kills"] or 0

        cur = conn.execute(
            "SELECT MIN(bullets_used) AS rec FROM runs WHERE won = 1"
        )
        rec_row = cur.fetchone()
        record_bullets = rec_row["rec"] if rec_row["rec"] is not None else None

    win_rate = (wins / total * 100) if total else 0.0
    return {
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_bullets": total_bullets,
        "record_bullets": record_bullets,
        "total_kills": total_kills,
    }
