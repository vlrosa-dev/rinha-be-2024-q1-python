from contextlib import asynccontextmanager
from datetime import datetime

from pydantic import ValidationError

from rinha_backend_q1_python.db import database
from rinha_backend_q1_python.models import clientes
from rinha_backend_q1_python.models import clientes_transacoes
from rinha_backend_q1_python.schemas import RequestTransacao
from rinha_backend_q1_python.schemas import Transacao

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import insert
from sqlalchemy import desc

from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.responses import JSONResponse
from starlette.routing import Route

@asynccontextmanager
async def lifespan(app):
    await database.connect()
    yield
    await database.disconnect()

async def healthcheck(request):
    return Response(content='OK', status_code=200)

async def transacoes(request: Request):
    req_transacao_body = await request.json()
    id_params = request.query_params['id']

    try:
        transacao = RequestTransacao(**req_transacao_body)
    except ValidationError as error:
        return JSONResponse({ "body_error": error.json() }, status_code=422)

    async with database.transaction():
        query_cliente = select([clientes.c.id, clientes.c.limite, clientes.c.saldo]).where(clientes.c.id == id_params)
        row_cliente = await database.fetch_one(query_cliente)
        if not row_cliente:
            return Response(f"Cliente { id } não encontrado.", status_code=404)
        
        if transacao.tipo == 'd':
            novo_saldo = int(row_cliente['saldo']) - int(transacao.valor)
        
        if transacao.tipo == 'c':
            novo_saldo = int(row_cliente['saldo']) + int(transacao.valor)

        if transacao.tipo == 'd' and novo_saldo < -row_cliente['limite']:
            raise Response("Transação inconsistente, saldo insuficiente.", status_code=422)
        
        query_update_saldo = update(clientes).where(clientes.c.id == id)
        await database.execute(query_update_saldo, { "saldo": novo_saldo })

        await database.execute(insert(clientes_transacoes).values(
            valor=transacao.valor,
            tipo=transacao.tipo,
            descricao=transacao.descricao,
            cliente_id=id
        ))
    
    return JSONResponse(
        { 
            "limite": row_cliente['limite'], 
            "saldo": novo_saldo 
        },
        status_code=200
    )

async def extrato(request):
    id_cliente = request.path_params['id']

    query_cliente = select([clientes.c.id, clientes.c.limite, clientes.c.saldo]).where(clientes.c.id == id_cliente)
    row_cliente = await database.fetch_one(query_cliente)
    if not row_cliente:
        raise Response("Cliente { id } não encontrado.", status_code=404)
    
    query_transacao = select(
        [
            clientes_transacoes.c.valor, 
            clientes_transacoes.c.tipo, 
            clientes_transacoes.c.descricao,
            clientes_transacoes.c.realizada_em
        ])\
            .where(clientes_transacoes.c.cliente_id == id_cliente)\
            .order_by(desc(clientes_transacoes.c.realizada_em))\
            .limit(10)
    rows_transacoes = await database.fetch_all(query_transacao)
    ultimas_transacoes = [ Transacao(**item) for item in rows_transacoes ]
    
    return JSONResponse(
        content={
            "saldo": {
                "total": row_cliente["saldo"],
                "data_extrato": str(datetime.utcnow()),
                "limite": row_cliente["limite"]
            }, "ultimas_transacoes": ultimas_transacoes
        },
        status_code=200
    )

routes = [
    Route('/healthcheck', endpoint=healthcheck, methods=['GET']),
    Route('/clientes/{id:int}/transacoes', endpoint=transacoes, methods=['POST']),
    Route('/clientes/{id:int}/extrato', endpoint=extrato, methods=['GET'])
]

app = Starlette(
    debug=True,
    routes=routes,
    lifespan=lifespan
)