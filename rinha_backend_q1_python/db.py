from databases import Database
from sqlalchemy import MetaData
from sqlalchemy import create_engine

URL_DATABASE = 'postgresql+psycopg2://postgres:1234@localhost:5432/postgres'

metadata_obj = MetaData()

database = Database(URL_DATABASE)

engine_db = create_engine(url=URL_DATABASE)