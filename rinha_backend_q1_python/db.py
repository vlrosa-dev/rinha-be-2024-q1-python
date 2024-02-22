from databases import Database
from sqlalchemy import MetaData
from sqlalchemy import create_engine

URL_DATABASE = 'postgresql+psycopg2://postgres:112131@db:5432/rinha_backend'

metadata_obj = MetaData()

database = Database(URL_DATABASE)

engine_db = create_engine(url=URL_DATABASE)