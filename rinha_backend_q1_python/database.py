import asyncpg
import contextlib

from starlette.applications import Starlette
from starlette.config import Config

from rinha_backend_q1_python.queries import TRUNCATE_TRANSACOES
from rinha_backend_q1_python.queries import ATUALIZA_SALDO

config = Config(".env")
DATABASE_URL = config.get("DATABASE_URL")
DATABASE_HOST = config.get("DATABASE_HOST")
DATABASE_USER = config.get("DATABASE_USER")
DATABASE_PASSWORD = config.get("DATABASE_PASSWORD")
DATABASE_PORT = config.get("DATABASE_PORT")
DATABASE_NAME = config.get("DATABASE_NAME")

@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    app.state.pool = await asyncpg.create_pool(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        min_size=5,
        max_size=20,
        max_queries=150000,
        max_inactive_connection_lifetime=300
    )

    async with app.state.pool.acquire() as conn:
        await conn.execute(TRUNCATE_TRANSACOES)
        await conn.execute(ATUALIZA_SALDO)
    yield
    await app.state.pool.close()