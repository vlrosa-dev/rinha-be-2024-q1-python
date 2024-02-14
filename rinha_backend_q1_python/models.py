import sqlalchemy as sa

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Clientes(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(sa.String(256))
    limite: Mapped[int] = mapped_column(sa.Integer)
    saldo: Mapped[int] = mapped_column(sa.Integer, default=0)

    def __repr__(self) -> str:
        return (
            f"<clientes,"
            f"id={self.id}", 
            f"nome={self.nome}"
            f"limite={self.limite}"
            f"saldo={self.saldo}>"
        )

    class Config:
        orm_mode = True

class ClientesTransacoes(Base):
    __tablename__ = 'clientes_transacoes'

    id: Mapped[int] = mapped_column(sa.Integer, autoincrement=True, primary_key=True)
    valor: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(sa.String(1), nullable=False)
    descricao: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    realizada_em: Mapped[str] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow())

    id_cliente: Mapped[int] = mapped_column(sa.ForeignKey('clientes.id'))

    def __repr__(self) -> str:
        return (
            f"<clientes_transacoes,"
            f"id={self.id}", 
            f"valor={self.valor}"
            f"tipo={self.tipo}"
            f"descricao={self.descricao}"
            f"realizada_em={self.realizada_em}>"
        )

    class Config:
        orm_mode = True