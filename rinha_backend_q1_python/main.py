from rinha_backend_q1_python.database import lifespan

from rinha_backend_q1_python.models import InfoSaldo
from rinha_backend_q1_python.models import RequestTransacao
from rinha_backend_q1_python.models import ResponseTransacoes
from rinha_backend_q1_python.models import Transacao

from rinha_backend_q1_python.queries import USUARIO_EXISTE
from rinha_backend_q1_python.queries import ULTIMAS_TRANSACOES
from rinha_backend_q1_python.queries import REALIZAR_TRANSACAO
from rinha_backend_q1_python.queries import SALDO_CLIENTE

from starlette.applications import Starlette
from starlette.responses import Response
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from asyncpg.exceptions import RaiseError
from pydantic import ValidationError

async def healthcheck(request):
    return Response(content='OK', status_code=200)

async def transacoes(request: Request):
    req_transacao_body = await request.json()
    id_cliente = request.path_params.get('id', None)

    if id_cliente < 0 or id_cliente > 5:
        return JSONResponse({'detail': 'cliente não encontrado'}, status_code=404)
    
    async with request.app.state.pool.acquire() as conn:
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

    async with request.app.state.pool.acquire() as conn:
        if record_cliente := await conn.fetchrow(SALDO_CLIENTE, id_cliente):
            saldo = InfoSaldo(
                total=record_cliente.get('valor'),
                limite=record_cliente.get('limite')
            )
            
            records_transacoes = await conn.fetch(ULTIMAS_TRANSACOES, id_cliente)
            ultimas_transacoes = [
                Transacao(
                    valor=item.get('valor'),
                    tipo=item.get('tipo'),
                    descricao=item.get('descricao'),
                    realizada_em=item.get('realizada_em')
                )
                for item in records_transacoes
            ]
            
            info_transacoes = ResponseTransacoes(
                saldo=saldo, ultimas_transacoes=ultimas_transacoes
            ).model_dump()
            
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