USUARIO_EXISTE = """
SELECT * FROM clientes WHERE id = $1;
"""

ULTIMAS_TRANSACOES = """
SELECT c.valor, c.tipo, c.descricao, c.realizada_em
FROM transacoes as c
WHERE cliente_id = $1
ORDER BY c.realizada_em DESC
LIMIT 10;
"""

REALIZAR_TRANSACAO = """
SELECT * FROM realizar_transacao($1, $2, $3, $4, $5)
"""

SALDO_CLIENTE = """
SELECT s.valor, c.limite FROM clientes c
INNER JOIN saldos s ON s.cliente_id = c.id
WHERE c.id = $1
"""