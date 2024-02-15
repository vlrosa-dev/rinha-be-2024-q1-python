from contextlib import asynccontextmanager
from datetime import datetime
from databases import Database

from rinha_backend_q1_python.schemas import ClienteTransacaoCreate

from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi import FastAPI
import uvicorn

database = Database("sqlite:///rinha.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

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
    query_select_cliente = """
        SELECT * FROM clientes 
        WHERE id=:id
    """
    rows_cliente = await database.fetch_one(query=query_select_cliente), { "id": id }
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