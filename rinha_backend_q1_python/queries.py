USUARIO_EXISTE = """
SELECT * FROM clientes WHERE id = :id;
"""

TRANSACOES_CLIENTES = """
SELECT c.valor, c.tipo, c.descricao, c.realizada_em
FROM clientes_transacoes as c
WHERE cliente_id = :id
ORDER BY c.realizada_em DESC;
"""