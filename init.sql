CREATE TABLE IF NOT EXISTS clientes (
    "id"             SERIAL PRIMARY KEY,
    "nome"           VARCHAR(256) NOT NULL,
    "limite"         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS transacoes (
    "id"		     SERIAL PRIMARY KEY,
    "valor"          INTEGER NOT NULL,
    "tipo"           VARCHAR(1) NOT NULL,
    "descricao"      VARCHAR(10) NOT NULL,
    "realizada_em"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "cliente_id"     INTEGER NOT NULL,
    CONSTRAINT "clientes_fk" FOREIGN KEY ("cliente_id") REFERENCES clientes("id")
);

CREATE TABLE IF NOT EXISTS saldos (
	"id"	         SERIAL PRIMARY KEY,
	"valor"          INTEGER NOT NULL,
	"cliente_id" 	 INTEGER UNIQUE NOT NULL,
	CONSTRAINT "clientes_fk" FOREIGN KEY ("cliente_id") REFERENCES clientes("id")
);

DO $$
BEGIN
    INSERT INTO clientes (nome, limite)
    VALUES
        ('o barato sai caro', 1000 * 100),
        ('zan corp ltda', 800 * 100),
        ('les cruders', 10000 * 100),
        ('padaria joia de cocaia', 100000 * 100),
        ('kid mais', 5000 * 100);
    
    INSERT INTO saldos (cliente_id, valor) SELECT id, 0 FROM clientes;
END;
$$;

CREATE OR REPLACE FUNCTION
	realizar_transacao(ucliente_id INT, uvalor INT, utipo CHAR(1), udescricao VARCHAR(10), ulimite INT, OUT sa INT)
LANGUAGE 
	plpgsql 
AS $$
DECLARE 
	saldo_atual INTEGER;
	novo_saldo INTEGER;
BEGIN
    SELECT s.valor 
	INTO saldo_atual 
	FROM saldos s
	WHERE cliente_id = ucliente_id 
	FOR UPDATE;
	
    IF utipo = 'd' THEN
		novo_saldo := saldo_atual + (uvalor * -1);
		IF novo_saldo < (ulimite * -1) THEN
        	RAISE EXCEPTION 'saldo insuficiente';
		END IF;
	ELSE
		novo_saldo := saldo_atual + uvalor;
    END IF;
	
    UPDATE saldos SET valor = novo_saldo WHERE cliente_id = ucliente_id;
    INSERT INTO transacoes (cliente_id, valor, tipo, descricao)
	VALUES (ucliente_id, uvalor, utipo, udescricao);
	
    sa := novo_saldo;
    RETURN;
END;
$$;