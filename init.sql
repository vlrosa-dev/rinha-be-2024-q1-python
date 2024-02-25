CREATE TABLE IF NOT EXISTS clientes (
    "id"             SERIAL,
    "nome"           VARCHAR(50) NOT NULL,
    "limite"         INT NOT NULL,
    "saldo"          INT DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS clientes_transacoes (
    "id"             SERIAL,
    "valor"          INT NOT NULL,
    "tipo"           VARCHAR(1) NOT NULL,
    "descricao"      VARCHAR(10) NOT NULL,
    "realizada_em"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "cliente_id"     INT NOT NULL,
    CONSTRAINT "clientes_fk" FOREIGN KEY ("cliente_id") REFERENCES clientes("id"),
    PRIMARY KEY (id)
);

CREATE OR REPLACE FUNCTION realizar_transacao(ucliente_id INT, uvalor INT, utipo CHAR(1), udescricao VARCHAR(10))
	RETURNS TABLE(limite INT, novosaldo INT)
	LANGUAGE plpgsql
AS $$
DECLARE
	vsaldo INT;
	vlimite INT;
	vstatus BOOLEAN;
	vnovosaldo INT;
BEGIN
	vstatus := true;
	
	SELECT c.limite as limite, c.saldo as saldo
	INTO vlimite, vsaldo
	FROM clientes as c
	WHERE c.id = ucliente_id FOR UPDATE;
	
	IF utipo = 'd' THEN
		vnovosaldo := vsaldo - uvalor;
		
		IF vnovosaldo < -vlimite THEN
			RAISE EXCEPTION 'Transação inconsistente, saldo insuficiente';
		
		END IF;
	ELSE
		vnovosaldo := vsaldo + uvalor;
	END IF;
	
	IF vstatus = true THEN
		UPDATE clientes as c SET saldo = vnovosaldo WHERE c.id = ucliente_id;
		INSERT INTO clientes_transacoes (cliente_id, valor, tipo, descricao) 
		VALUES (ucliente_id, uvalor, utipo, udescricao);
	END IF;
	
	RETURN QUERY SELECT c.limite, c.saldo FROM clientes c WHERE c.id = ucliente_id;
END;
$$;

INSERT INTO clientes ("nome", "limite")
VALUES
    ('grupo avanti', 1000 * 100),
    ('grupo itau', 800 * 100),
    ('grupo caixa', 10000 * 100),
    ('padaria do zé', 100000 * 100),
    ('padaria do tonico', 5000 * 100);