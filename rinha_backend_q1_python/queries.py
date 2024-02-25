USUARIO_EXISTE = """
SELECT * FROM clientes WHERE id = :id;
"""

ULTIMAS_TRANSACOES = """
SELECT c.valor, c.tipo, c.descricao, c.realizada_em
FROM clientes_transacoes as c
WHERE cliente_id = :id
ORDER BY c.realizada_em DESC;
"""

REALIZAR_TRANSACAO = """
SELECT * FROM realizar_transacao(:id, :valor, :tipo, :descricao)
"""