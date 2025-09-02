from contextlib import asynccontextmanager
import aiosqlite
from pathlib import Path

# Указываю на корень проекта в parents[1]
DB_PATH = (Path(__file__).resolve().parents[1] / "asic.db").as_posix()

@asynccontextmanager
async def db_connection():
    """Функция для подключения к БД"""
    db = await aiosqlite.connect(DB_PATH)
    try:
        db.row_factory = aiosqlite.Row
        yield db
    finally:
        await db.close()



async def get_user(nickname: str, tg_id: int) -> bool:
    """Функция для определения доступа к боту"""

    async with db_connection() as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE nickname = ? AND tg_id = ? LIMIT 1", (nickname, tg_id))

        if await cursor.fetchone():
            return True
        return False
