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
    connection.close()

def insert_tables():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
    """
    INSERT INTO clientes ("id", "nome", "limite")
    VALUES
        (1, 'grupo avanti', 1000 * 100),
        (2, 'grupo itau', 800 * 100),
        (3, 'grupo caixa', 10000 * 100),
        (4, 'padaria do zé', 100000 * 100),
        (5, 'padaria do tonico', 5000 * 100);
    """
    )
    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_tables()
    insert_tables()