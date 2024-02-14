from rinha_backend_q1_python.models import ClientesTransacoes
from rinha_backend_q1_python.models import Clientes
from rinha_backend_q1_python.models import Base

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:112131@localhost:5432/rinha_backend"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

def create_tables():
    with engine.begin() as connection:
        Base.metadata.create_all(
            bind=connection, 
            tables=[ Clientes.__table__, ClientesTransacoes.__table__ ],
            checkfirst=True
        )

def insert_tables():
    with engine.begin() as connection:
        connection.execute(
            insert(Clientes.__table__),
            [ 
                { "id": 1, "nome": "cliente_01", "limite": 1000 * 100 },
                { "id": 2, "nome": "cliente_02", "limite": 800 * 100 },
                { "id": 3, "nome": "cliente_03", "limite": 10000 * 100 },
                { "id": 4, "nome": "cliente_04", "limite": 100000 * 100 },
                { "id": 5, "nome": "cliente_05", "limite": 5000 * 100 },
            ]
        )
        connection.commit()

if __name__ == '__main__':
    create_tables()
    insert_tables()