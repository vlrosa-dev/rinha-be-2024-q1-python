from contextlib import asynccontextmanager
from datetime import datetime

from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi import FastAPI

from rinha_backend_q1_python.db import database
from rinha_backend_q1_python.models import clientes
from rinha_backend_q1_python.models import clientes_transacoes
from rinha_backend_q1_python.schemas import RequestTransacao

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import insert

import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    
    query = clientes.insert()
    values = [
        {"id": 1, "nome": "ze", "limite": 100000, "saldo": 0},
        {"id": 2, "nome": "junin", "limite": 80000, "saldo": 0},
        {"id": 3, "nome": "clebin", "limite": 1000000, "saldo": 0},
        {"id": 4, "nome": "padoca", "limite": 10000000, "saldo": 0},
        {"id": 5, "nome": "empresa", "limite": 500000, "saldo": 0}
    ]
    await database.execute_many(query=query, values=values)

    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

@app.post(path="/clientes/{id}/transacoes", status_code=200)
async def transacoes(id: int, transacao: RequestTransacao):
    query_cliente = select([clientes.c.id, clientes.c.limite, clientes.c.saldo]).where(clientes.c.id == id)
    row_cliente = await database.fetch_one(query_cliente)
    if not row_cliente:
        raise HTTPException(status_code=404, detail=f"Cliente { id } não encontrado.")

    if transacao.tipo == 'd':
        novo_saldo = int(row_cliente['saldo']) - int(transacao.valor)
    
    if transacao.tipo == 'c':
        novo_saldo = int(row_cliente['saldo']) + int(transacao.valor)

    if transacao.tipo == 'd' and novo_saldo < -row_cliente['limite']:
        raise HTTPException(status_code=422, detail="Transação inconsistente, saldo insuficiente.")
    
    query_update_saldo = update(clientes).where(clientes.c.id == id)
    await database.execute(query_update_saldo, { "saldo": novo_saldo })

    await database.execute(insert(clientes_transacoes).values(
        valor=transacao.valor,
        tipo=transacao.tipo,
        descricao=transacao.descricao,
        cliente_id=id
    ))
    
    return JSONResponse({ "limite": row_cliente['limite'], "saldo": novo_saldo })

@app.post(path="/clientes/{id}/extrato")
async def extrato(id: int):
    ##### Verifica se cliente existe
    query_select_cliente = """
        SELECT * FROM clientes 
        WHERE id=:id
    """
    cliente = await database.fetch_one(query_select_cliente, { "id": id })
    if len(cliente) < 1:
        raise HTTPException(
            status_code=404, detail=f"Cliente { id } não encontrado"
        )
    
    ##### Consulta transacoes do cliente
    ultimas_transacoes = []
    clientes_transacoes = """
        SELECT valor, tipo, descricao, realizada_em  
        FROM clientes_transacoes
        WHERE id_cliente=:id
        ORDER BY realizada_em DESC
        LIMIT 10
    """
    result_transacoes = await database.fetch_all(clientes_transacoes, { "id": id })
    if len(result_transacoes) > 0:
        for item in result_transacoes:
            ultimas_transacoes.append(
                {
                    "valor": item[0],
                    "tipo": item[1],
                    "descricao": item[2],
                    "realizada_em": item[3]
                }
            )
    
    ##### Configura JSON de resposta
    result_json = {
        "saldo": {
            "total": cliente[3],
            "data_extrato": str(datetime.utcnow()),
            "limite": cliente[2]
        }, "ultimas_transacoes": ultimas_transacoes
    }

    return JSONResponse(content=result_json, status_code=200)

if __name__ == '__main__':
    uvicorn.run(
        app="rinha_backend_q1_python.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )