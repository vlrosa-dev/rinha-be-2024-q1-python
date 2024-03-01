from pydantic import BaseModel
from pydantic import field_serializer
from pydantic import Field

from datetime import datetime
from enum import Enum
from typing import Literal

class EnumTipoTransacao(str, Enum):
    credito = 'c'
    debito = 'd'

class RequestTransacao(BaseModel):
    valor: int = Field(gt=0)
    tipo: EnumTipoTransacao = Field(description='C - Credito / D - Debito')
    descricao: str = Field(description='Motivo da transação', min_length=1, max_length=10)

class Transacao(BaseModel):
    valor: int
    tipo: Literal['c', 'd']
    descricao: str
    realizada_em: datetime

    @field_serializer('realizada_em')
    def serialize_dt_realizada(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

class InfoSaldo(BaseModel):
    total: int
    data_extrato: datetime = Field(default_factory=datetime.utcnow)
    limite: int

    @field_serializer('data_extrato')
    def serialize_dt_extrato(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

class ResponseTransacoes(BaseModel):
    saldo: InfoSaldo
    ultimas_transacoes: list[Transacao]