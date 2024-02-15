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
    "id_cliente"      INT NOT NULL,
    CONSTRAINT "clients_fk" FOREIGN KEY ("id_cliente") REFERENCES clients("id")
);

DO $$
BEGIN
    INSERT INTO clientes ("nome", "limite")
    VALUES
        ('grupo avanti', 1000 * 100),
        ('grupo itau', 800 * 100),
        ('grupo caixa', 10000 * 100),
        ('padaria do zé', 100000 * 100),
        ('padaria do tonico', 5000 * 100);
END; $$