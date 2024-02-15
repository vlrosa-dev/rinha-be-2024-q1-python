from contextlib import asynccontextmanager
from datetime import datetime
from databases import Database

from typing import Annotated
from sqlalchemy.orm import Session

from rinha_backend_q1_python.schemas import ClienteTransacaoCreate
#from rinha_backend_q1_python.models import Clientes
#from rinha_backend_q1_python.models import ClientesTransacoes
#from rinha_backend_q1_python.db import get_session

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from fastapi import FastAPI
from fastapi import Depends

import uvicorn

database = Database("sqlite:///rinha.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
#Session_Db = Annotated[Session, Depends(get_session)]

@app.post(path="/clientes/{id}/transacoes", status_code=200)
async def transacoes(id: int, transacao: ClienteTransacaoCreate):
    ##### Validação simples dos dados recebidos
    if transacao.valor <= 0:
        raise HTTPException(
            status_code=422, detail="O campo 'valor' deve ser maior que 0."
        )
    
    if (transacao.tipo != 'c') and (transacao.tipo != "d"):
        raise HTTPException(
            status_code=422, detail="O campo 'tipo' deve ser 'c=credito' ou 'd=debito'."
        )
    
    if (len(transacao.descricao) <= 0) or (len(transacao.descricao) > 10):
        raise HTTPException(
            status_code=422, detail="O campo 'descricao' deve ter entre 1 a 10 caracteres."
        )
    
    ##### Verifica se cliente existe na base de dados
    query_select_cliente = f"""
        SELECT * FROM clientes 
        WHERE id={id}
    """
    rows_cliente = await database.fetch_one(query=query_select_cliente)
    if len(rows_cliente) < 1:
        raise HTTPException(status_code=404, detail=f"Cliente ({ id }) não encontrado.")

    id_cliente = int(rows_cliente[0])
    limite_cliente = int(rows_cliente[2])
    saldo_cliente = int(rows_cliente[3])

    if transacao.tipo == 'd':
        novo_saldo = int(saldo_cliente) - int(transacao.valor)
    
    if transacao.tipo == 'c':
        novo_saldo = int(saldo_cliente) + int(transacao.valor)

    if abs(novo_saldo) > limite_cliente:
        raise HTTPException(status_code=422, detail="Transação não será efetuada.")
    
    ##### Atualiza o saldo do cliente
    query_update_cliente = """
        UPDATE clientes 
        SET saldo=:novo_saldo
        WHERE id=:id
    """
    values_update_cliente = {
        "novo_saldo": novo_saldo,
        "id": id_cliente
    }
    await database.execute(query_update_cliente, values_update_cliente)

    ##### Insere linha de transação
    query_insert_transacao = """
        INSERT INTO clientes_transacoes
            (valor, tipo, descricao, id_cliente) 
        VALUES 
            (:valor, :tipo, :descricao, :id_cliente)
    """
    values_insert_transacao = {
        "valor": transacao.valor,
        "tipo": transacao.tipo,
        "descricao": transacao.descricao, 
        "id_cliente": id_cliente
    }
    await database.execute(query_insert_transacao, values_insert_transacao)

    ##### Consulta Cliente após atualização
    query_select_cliente = f"""
        SELECT * FROM clientes 
        WHERE id={id}
    """
    cliente_att = await database.fetch_one(query_select_cliente)
    
    return JSONResponse(
        { 
            "limite": cliente_att[2], 
            "saldo": cliente_att[3]
        }
    )

# @app.post(path="/clientes/{id}/extrato")
# async def extrato(session: Session_Db, id: int):
#     cliente = session\
#         .query(Clientes)\
#         .filter(Clientes.id == id)\
#         .first()

#     if not cliente:
#         raise HTTPException(
#             status_code=404, detail=f"Cliente { id } não encontrado"
#         )
    
#     clientes_transacoes = session\
#         .query(ClientesTransacoes)\
#         .filter(ClientesTransacoes.id_cliente == id)\
#         .all()
    
#     conteudo_json = {
#         "saldo": {
#             "total": cliente.saldo,
#             "data_extrato": str(datetime.utcnow()),
#             "limite": cliente.limite
#         },
#         "ultimas_transacoes": jsonable_encoder(clientes_transacoes)
#     }

#     return JSONResponse(content=conteudo_json, status_code=200)

if __name__ == '__main__':
    uvicorn.run(
        app="rinha_backend_q1_python.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )