from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from rinha_backend_q1_python.db import database
from rinha_backend_q1_python.models import clientes
from rinha_backend_q1_python.models import clientes_transacoes
from rinha_backend_q1_python.schemas import RequestTransacao

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import insert
from sqlalchemy import desc

import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get('/healthcheck')
async def health_check():
    return JSONResponse(status_code=200)

@app.post(path="/clientes/{id}/transacoes", status_code=200)
async def transacoes(id: int, transacao: RequestTransacao):
    async with database.transaction():
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

@app.get(path="/clientes/{id}/extrato")
async def extrato(id: int):
    query_cliente = select([clientes.c.id, clientes.c.limite, clientes.c.saldo]).where(clientes.c.id == id)
    row_cliente = await database.fetch_one(query_cliente)
    if not row_cliente:
        raise HTTPException(status_code=404, detail=f"Cliente { id } não encontrado.")
    
    query_transacao = select(
        [
            clientes_transacoes.c.valor, 
            clientes_transacoes.c.tipo, 
            clientes_transacoes.c.descricao,
            clientes_transacoes.c.realizada_em
        ])\
            .where(clientes_transacoes.c.cliente_id == id)\
            .order_by(desc(clientes_transacoes.c.realizada_em))\
            .limit(10)
    rows_transacoes = await database.fetch_all(query_transacao)

    ultimas_transacoes = []
    for transacao in rows_transacoes:
        ultimas_transacoes.append({
            "valor": transacao["valor"],
            "tipo": transacao["tipo"],
            "descricao": transacao["descricao"],
            "realizada_em": transacao["realizada_em"]
    })
    
    return {
        "saldo": {
            "total": row_cliente["saldo"],
            "data_extrato": datetime.utcnow(),
            "limite": row_cliente["limite"]
        }, "ultimas_transacoes": ultimas_transacoes
    }

if __name__ == '__main__':
    uvicorn.run(
        app="rinha_backend_q1_python.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True
    )