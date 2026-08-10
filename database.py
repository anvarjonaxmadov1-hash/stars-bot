import asyncpg
from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def init_db():
    await get_pool()


async def set_user(user_id: int, username: str, referred_by: int | None = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username, referred_by)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET username = excluded.username
            """,
            user_id, username, referred_by,
        )


async def count_referrals(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT COUNT(*) AS cnt FROM users WHERE referred_by=$1", user_id)
        return row["cnt"] if row else 0


async def get_referrer(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT referred_by FROM users WHERE user_id=$1", user_id)
        return row["referred_by"] if row and row["referred_by"] else None


async def get_balance(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
        return row["balance"] if row else 0


async def add_balance(user_id: int, amount: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET balance = balance + $1 WHERE user_id=$2", amount, user_id)


async def use_balance(user_id: int, max_amount: int) -> int:
    current = await get_balance(user_id)
    used = min(current, max_amount)
    if used > 0:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance = balance - $1 WHERE user_id=$2", used, user_id)
    return used


async def set_lang(user_id: int, lang: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET lang=$1 WHERE user_id=$2", lang, user_id)


async def get_lang(user_id: int) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT lang FROM users WHERE user_id=$1", user_id)
        return row["lang"] if row else "uz"


async def create_order(user_id: int, item: str, price: int, method: str, discount_used: int = 0) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO orders (user_id, item, price, method, discount_used)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING order_id
            """,
            user_id, item, price, method, discount_used,
        )
        return row["order_id"]


async def update_order_status(order_id: int, status: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET status=$1 WHERE order_id=$2", status, order_id)


async def get_order(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT order_id, user_id, item, price, method, status, discount_used, bonus_given
            FROM orders WHERE order_id=$1
            """,
            order_id,
        )
        if not row:
            return None
        return (
            row["order_id"], row["user_id"], row["item"], row["price"],
            row["method"], row["status"], row["discount_used"], row["bonus_given"],
        )


async def mark_bonus_given(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET bonus_given=1 WHERE order_id=$1", order_id)


async def get_user_orders(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT order_id, item, price, status FROM orders WHERE user_id=$1 ORDER BY order_id DESC",
            user_id,
        )
        return [(r["order_id"], r["item"], r["price"], r["status"]) for r in rows]
