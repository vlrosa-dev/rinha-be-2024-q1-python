from sqlalchemy.sql import func
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
    Column("id", Integer, primary_key=True),
    Column("nome", String(50)),
    Column("limite", Integer),
    Column("saldo", Integer)
)

clientes_transacoes = Table(
    "clientes_transacoes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cliente_id", Integer, ForeignKey("clientes.id")),
    Column("valor", Integer),
    Column("tipo", String(1)),
    Column("descricao", String(10)),
    Column("realizada_em", DateTime, default=func.now())
)