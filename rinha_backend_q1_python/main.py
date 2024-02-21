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
        raise HTTPException(status_code=404, detail=f"Cliente ({ id }) não encontrado.")

    id_cliente = row_cliente['id']
    limite_cliente = row_cliente['limite']
    saldo_cliente = row_cliente['saldo']

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
    query_select_cliente = """
        SELECT * FROM clientes 
        WHERE id=:id
    """
    cliente_att = await database.fetch_one(query_select_cliente, { "id": id})
    
    return JSONResponse(
        { 
            "limite": cliente_att[2], 
            "saldo": cliente_att[3]
        }
    )

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