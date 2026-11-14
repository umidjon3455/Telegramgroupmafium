import aiosqlite
from .config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT NOT NULL,
                games INTEGER NOT NULL DEFAULT 0,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                xp INTEGER NOT NULL DEFAULT 0
            )
        """)
        await db.commit()

async def register_player(user):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO players(user_id, username, full_name)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 username=excluded.username, full_name=excluded.full_name""",
            (user.id, user.username, user.full_name),
        )
        await db.commit()

async def record_game(players, winners):
    winner_ids = set(winners)
    async with aiosqlite.connect(DB_PATH) as db:
        for player in players.values():
            won = player["id"] in winner_ids
            await db.execute(
                """INSERT INTO players(user_id, username, full_name, games, wins, losses, xp)
                   VALUES (?, ?, ?, 1, ?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET
                     username=excluded.username,
                     full_name=excluded.full_name,
                     games=players.games+1,
                     wins=players.wins+excluded.wins,
                     losses=players.losses+excluded.losses,
                     xp=players.xp+excluded.xp""",
                (player["id"], player.get("username"), player["name"],
                 int(won), int(not won), 30 if won else 10),
            )
        await db.commit()

async def get_profile(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def get_top(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM players ORDER BY wins DESC, xp DESC LIMIT ?", (limit,)
        )
        return await cur.fetchall()
