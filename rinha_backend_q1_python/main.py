from datetime import datetime
import uvicorn

from typing import Annotated
from sqlalchemy.orm import Session

from rinha_backend_q1_python.schemas import ClienteTransacaoCreate
from rinha_backend_q1_python.models import Clientes
from rinha_backend_q1_python.models import ClientesTransacoes
from rinha_backend_q1_python.db import get_session

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from fastapi import FastAPI
from fastapi import Depends

app = FastAPI()
Session_Db = Annotated[Session, Depends(get_session)]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post(path="/clientes/{id}/transacoes", status_code=200)
async def transacoes(session: Session_Db, id: int, transacao: ClienteTransacaoCreate):
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
    
    cliente = session\
        .query(Clientes)\
        .filter(Clientes.id == id)\
        .first()

    if not cliente:
        raise HTTPException(
            status_code=404, detail=f"Cliente { id } não encontrado"
        )
    
    if transacao.tipo == 'd':
        novo_saldo = int(cliente.saldo) - (int(transacao.valor) * 100)
        if novo_saldo > cliente.limite:
            raise HTTPException(
                status_code=422, detail="Transação não será efetuada."
            )
    elif transacao.tipo == 'c':
        novo_saldo = int(cliente.saldo) + (int(transacao.valor) * 100)
    
    cliente_transacao = ClientesTransacoes(
        valor=transacao.valor * 100,
        tipo=transacao.tipo,
        descricao=transacao.descricao,
        id_cliente=cliente.id
    )
    session.add(cliente_transacao)
    session.commit()
    session.refresh(cliente_transacao)

    cliente.saldo = novo_saldo
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return JSONResponse(
        { "limite": cliente.limite, "saldo": cliente.saldo }
    )

@app.post(path="/clientes/{id}/extrato")
async def extrato(session: Session_Db, id: int):
    cliente = session\
        .query(Clientes)\
        .filter(Clientes.id == id)\
        .first()

    if not cliente:
        raise HTTPException(
            status_code=404, detail=f"Cliente { id } não encontrado"
        )
    
    clientes_transacoes = session\
        .query(ClientesTransacoes)\
        .filter(ClientesTransacoes.id_cliente == id)\
        .all()
    
    conteudo_json = {
        "saldo": {
            "total": cliente.saldo,
            "data_extrato": str(datetime.utcnow()),
            "limite": cliente.limite
        },
        "ultimas_transacoes": jsonable_encoder(clientes_transacoes)
    }

    return JSONResponse(content=conteudo_json, status_code=200)

if __name__ == '__main__':
    uvicorn.run(
        app="rinha_backend_q1_python.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )