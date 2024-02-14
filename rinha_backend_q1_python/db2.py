import sqlite3

def create_connection():
    connection = sqlite3.connect("rinha.db")
    return connection

def create_tables():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL,
        nome VARCHAR(50) NOT NULL,
        limite INT NOT NULL,
        saldo INT DEFAULT 0,
        PRIMARY KEY (id)
    );""")

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS clientes_transacoes (
        id SERIAL,
        valor INT NOT NULL,
        tipo VARCHAR(1) NOT NULL,
        descricao VARCHAR(10) NOT NULL,
        realizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        id_cliente INT NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT "clientes_fk" FOREIGN KEY ("id_cliente") REFERENCES clientes("id")
    );""")

if __name__ == '__main__':
    create_tables()