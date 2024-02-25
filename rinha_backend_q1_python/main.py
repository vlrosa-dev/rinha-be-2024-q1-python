from rinha_backend_q1_python.models import (
    clientes,
    clientes_transacoes
)

from rinha_backend_q1_python.schemas import (
    InfoSaldo,
    ResponseTransacoes,
    RequestTransacao, 
    Transacao
)

from rinha_backend_q1_python.queries import (
    USUARIO_EXISTE, 
    TRANSACOES_CLIENTES
)
from rinha_backend_q1_python.db import database

from sqlalchemy import (
    update,
    insert
)

from starlette.responses import (
    Response,
    JSONResponse
)
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route

from contextlib import asynccontextmanager
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
    
    if not (id_cliente := request.path_params.get('id', None)):
        return JSONResponse({'detail': 'cliente não encontrado'}, status_code=404)
    
    async with database.transaction():
        if record_cliente := await database.fetch_one(USUARIO_EXISTE, { "id": id_cliente }):
            try:
                transacao = RequestTransacao(**req_transacao_body)
            except ValidationError as error:
                return JSONResponse({ "detail": error.json() }, status_code=422)
        
        novo_saldo = int(record_cliente['saldo']) + \
            (-transacao.valor if 'd' in transacao.tipo else +transacao.valor)
        
        if (novo_saldo < -record_cliente['limite']) and ('d' in transacao.tipo):
            return JSONResponse({"detail": "Transação inconsistente, saldo insuficiente."}, status_code=422)
        
        query_update_saldo = update(clientes).where(clientes.c.id == id_cliente)
        await database.execute(query_update_saldo, { "saldo": novo_saldo })

        await database.execute(insert(clientes_transacoes).values(
            valor=transacao.valor,
            tipo=transacao.tipo,
            descricao=transacao.descricao,
            cliente_id=id_cliente
        ))
    
    return JSONResponse({ "limite": record_cliente['limite'], "saldo": novo_saldo }, status_code=200)

async def extrato(request: Request):
    id_cliente = request.path_params['id']

    async with database.transaction():
        if record_cliente := await database.fetch_one(USUARIO_EXISTE, { "id": id_cliente }):
            info_saldo = InfoSaldo(
                total=record_cliente['saldo'],
                limite=record_cliente['limite']
            )
            
            records_transacoes = await database.fetch_all(TRANSACOES_CLIENTES, { "id": id_cliente })
            ultimas_transacoes = [
                Transacao(valor=item.valor, 
                          tipo=item.tipo, 
                          descricao=item.descricao, 
                          realizada_em=item.realizada_em
                        )
                for item in records_transacoes
            ]
            
            info_transacoes = ResponseTransacoes(saldo=info_saldo, ultimas_transacoes=ultimas_transacoes)
            return JSONResponse(info_transacoes.model_dump_json(), status_code=200)
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