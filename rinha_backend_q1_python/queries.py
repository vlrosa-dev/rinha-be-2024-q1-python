USUARIO_EXISTE = """
SELECT * FROM clientes WHERE id = :cliente_id;
"""

ULTIMAS_TRANSACOES = """
SELECT c.valor, c.tipo, c.descricao, c.realizada_em
FROM clientes_transacoes as c
WHERE cliente_id = :id
ORDER BY c.realizada_em DESC
LIMIT 10;
"""

REALIZAR_TRANSACAO = """
SELECT * FROM realizar_transacao(:cliente_id, :valor, :tipo, :descricao, :limite)
"""