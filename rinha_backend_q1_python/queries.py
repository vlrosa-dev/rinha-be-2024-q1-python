USUARIO_EXISTE = """
SELECT * FROM clientes WHERE id = :cliente_id;
"""

ULTIMAS_TRANSACOES = """
SELECT c.valor, c.tipo, c.descricao, c.realizada_em
FROM transacoes as c
WHERE cliente_id = :cliente_id
ORDER BY c.realizada_em DESC
LIMIT 10;
"""

REALIZAR_TRANSACAO = """
SELECT * FROM realizar_transacao(:cliente_id, :valor, :tipo, :descricao, :limite)
"""

SALDO_CLIENTE = """
SELECT s.valor, c.limite FROM clientes c
INNER JOIN saldos s ON s.cliente_id = c.id
WHERE c.id = :cliente_id
"""