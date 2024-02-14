from pydantic import BaseModel

class ClienteTransacaoCreate(BaseModel):
    valor: int
    tipo: str
    descricao: str

class ClienteTransacoesRead(BaseModel):
    valor: int
    tipo: str
    descricao: str
    realizada_em: str

class ClienteTransacoesList(BaseModel):
    ultimas_transacoes: list[ClienteTransacoesRead]

class ClientesRead(BaseModel):
    id: int
    nome: str
    limite: int
    saldo: int