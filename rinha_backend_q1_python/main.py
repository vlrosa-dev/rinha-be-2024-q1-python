from rinha_backend_q1_python.schemas import (
    RequestTransacao
)

from rinha_backend_q1_python.queries import (
    USUARIO_EXISTE, 
    ULTIMAS_TRANSACOES,
    REALIZAR_TRANSACAO,
    SALDO_CLIENTE
)

from starlette.responses import (
    Response,
    JSONResponse
)
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route

from asyncpg import create_pool
from asyncpg.exceptions import RaiseError

from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import ValidationError

DB_CONFIG = {
    'host': 'db',
    'user': 'postgres',
    'password': '112131',
    'port': 5432,
    'database': 'rinha_backend',
    "min_size": 1,
    "max_size": 20,

}

@asynccontextmanager
async def lifespan(app):
    app.pool = await create_pool(**DB_CONFIG, max_inactive_connection_lifetime=300)
    yield
    app.pool.close()

async def healthcheck(request):
    return Response(content='OK', status_code=200)

async def transacoes(request: Request):
    req_transacao_body = await request.json()
    id_cliente = request.path_params.get('id', None)

    if id_cliente < 0 or id_cliente > 5:
        return JSONResponse({'detail': 'cliente não encontrado'}, status_code=404)
    
    async with request.app.pool.acquire() as conn:
        if result_cliente := await conn.fetchrow(USUARIO_EXISTE, id_cliente):
            try:
                transacao = RequestTransacao(**req_transacao_body)
                result_transacao = await conn.fetchval(
                    REALIZAR_TRANSACAO,
                    id_cliente, 
                    transacao.valor,
                    transacao.tipo,
                    transacao.descricao,
                    result_cliente['limite']
                )

                return JSONResponse(
                    { "limite": result_cliente['limite'],
                      "saldo": result_transacao
                    }, 
                    status_code=200
                )

            except ValidationError as error:
                return JSONResponse({ "detail": error.json() }, status_code=422)
            
            except RaiseError as error:
                if 'saldo insuficiente' in str(error):
                    return JSONResponse({ "detail": "Transação inconsistente, saldo insuficiente" }, status_code=422)
            
            except Exception as error:
                return JSONResponse({ "detail": error }, status_code=422)

        else:
            return Response(f"Cliente { id_cliente } não encontrado.", status_code=404)
        
async def extrato(request: Request):
    id_cliente = request.path_params['id']

    if id_cliente < 0 or id_cliente > 5:
        return JSONResponse({'detail': 'cliente não encontrado'}, status_code=404)

    async with request.app.pool.acquire() as conn:
        if record_cliente := await conn.fetchrow(SALDO_CLIENTE, id_cliente):
            info_saldo = {
                "saldo": int(record_cliente['valor']),
                "limite": int(record_cliente['limite']),
                "data_extrato": str(datetime.utcnow())
            }
            
            records_transacoes = await conn.fetch(ULTIMAS_TRANSACOES, id_cliente)
            ultimas_transacoes = [
                { "valor": int(item['valor']), 
                  "tipo": str(item['tipo']), 
                  "descricao": str(item['descricao']), 
                  "realizada_em": str(item['realizada_em']) }
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