from rinha_backend_q1_python.schemas import (
    RequestTransacao
)

from rinha_backend_q1_python.queries import (
    USUARIO_EXISTE, 
    ULTIMAS_TRANSACOES,
    REALIZAR_TRANSACAO
)
from rinha_backend_q1_python.db import database

from starlette.responses import (
    Response,
    JSONResponse
)
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route

from asyncpg.exceptions import RaiseError
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import ValidationError

@asynccontextmanager
async def lifespan(app):
    await database.connect()
    yield
    await database.disconnect()

async def healthcheck(request):
    return Response(content='OK', status_code=200)

async def transacoes(request: Request):
    req_transacao_body = await request.json()
    id_cliente = request.path_params.get('id', None)

    if id_cliente < 0 or id_cliente < 5:
        return JSONResponse({'detail': 'cliente não encontrado'}, status_code=404)
    
    async with database.transaction():
        if record_cliente := await database.fetch_one(USUARIO_EXISTE, { "cliente_id": id_cliente }):
            try:
                transacao = RequestTransacao(**req_transacao_body)

                rst_transacao = await database.fetch_one(
                    query=REALIZAR_TRANSACAO,
                    values={
                        "cliente_id": id_cliente, 
                        "valor": transacao.valor,
                        "tipo": transacao.tipo,
                        "descricao": transacao.descricao,
                        "limite": record_cliente['limite']
                    }
                )

                return JSONResponse({ "limite": record_cliente['limite'], "saldo": rst_transacao['novosaldo'] }, status_code=200)

            except ValidationError as error:
                return JSONResponse({ "detail": error.json() }, status_code=422)
            
            except RaiseError as error:
                if 'saldo insuficiente' in str(error):
                    return JSONResponse({ "detail": "Transação inconsistente, saldo insuficiente" }, status_code=422)
            
            except Exception as error:
                return JSONResponse({ "detail": error }, status_code=422)

async def extrato(request: Request):
    id_cliente = request.path_params['id']

    async with database.transaction():
        if record_cliente := await database.fetch_one(USUARIO_EXISTE, { "id": id_cliente }):
            info_saldo = {
                "saldo": int(record_cliente['saldo']),
                "limite": int(record_cliente['limite']),
                "data_extrato": str(datetime.utcnow())
            }
            
            records_transacoes = await database.fetch_all(ULTIMAS_TRANSACOES, { "id": id_cliente })
            ultimas_transacoes = [
                { "valor": int(item.valor), 
                  "tipo": str(item.tipo), 
                  "descricao": str(item.descricao), 
                  "realizada_em": str(item.descricao) }
                for item in records_transacoes
            ]
            
            info_transacoes = { "saldo": info_saldo, "ultimas_transacoes": ultimas_transacoes }
            return JSONResponse(info_transacoes, status_code=200)
        else:
            return Response(f"Cliente { id_cliente } não encontrado.", status_code=404)

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