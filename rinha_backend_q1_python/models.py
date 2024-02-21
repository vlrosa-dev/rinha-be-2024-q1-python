from rinha_backend_q1_python.db import engine_db
from sqlalchemy.sql import func
from sqlalchemy import text
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Table,
    MetaData,
    Integer,
    String
)

metadata_obj = MetaData()

clientes = Table(
    "clientes", 
    metadata_obj,
    Column("id", Integer, primary_key=True, unique=True),
    Column("nome", String(50), nullable=False),
    Column("limite", Integer),
    Column("saldo", Integer, server_default=text("0"))
)

clientes_transacoes = Table(
    "clientes_transacoes",
    metadata_obj,
    Column("id", Integer, primary_key=True, unique=True),
    Column("cliente_id", Integer, ForeignKey("clientes.id")),
    Column("valor", Integer),
    Column("tipo", String(1)),
    Column("descricao", String(10)),
    Column("realizada_em", DateTime, default=func.now())
)

if __name__ == '__main__':
    metadata_obj.drop_all(engine_db, tables=[clientes, clientes_transacoes])
    metadata_obj.create_all(engine_db, tables=[clientes, clientes_transacoes])