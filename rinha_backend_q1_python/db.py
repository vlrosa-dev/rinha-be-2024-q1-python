from databases import Database
from sqlalchemy import MetaData
from sqlalchemy import create_engine
import asyncpg
import asyncio

URL_DATABASE = 'postgresql+asyncpg://postgres:112131@db:5432/rinha_backend'

metadata_obj = MetaData()

#database = Database(URL_DATABASE, min_size=1, max_size=10)

engine_db = create_engine(url=URL_DATABASE)