"""
Definição das tabelas do banco de dados SQLite.
Este módulo contém as definições de todas as tabelas usadas no sistema.
"""

import sqlite3
import logging
import config

logger = logging.getLogger(config.APP_NAME)


def setup_database(db_path):
    """Configura o banco de dados e cria as tabelas necessárias"""
    conn = sqlite3.connect(db_path)
    
    # Criar as tabelas
    create_tables(conn)
    
    # Inserir dados de exemplo (se necessário)
    insert_sample_data(conn)
    
    return conn

def create_tables(conn: sqlite3.Connection):
    """
    Cria todas as tabelas necessárias no banco de dados.
    
    Args:
        conn: Conexão com o banco de dados SQLite
    """
    cursor = conn.cursor()

    # Habilitar chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON")

    # Tabela de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        document TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabela de veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT NOT NULL,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER,
        color TEXT,
        client_id INTEGER,
        brand_code TEXT,
        model_code TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (id)
    )
    ''')

    # Tabela de funcionários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        document TEXT NOT NULL,
        role TEXT,
        hire_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabela de peças
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        description TEXT NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        buy_price REAL,
        sell_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabela de ordens de serviço
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL,
        open_date TIMESTAMP,
        vehicle_id INTEGER,
        description TEXT,
        status TEXT,
        employee_id INTEGER,
        completion_date TIMESTAMP,
        total_value REAL,
        payment_method TEXT,
        client_signature BLOB,
        mechanic_signature BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')

    # Tabela de peças em ordens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        part_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES service_orders (id),
        FOREIGN KEY (part_id) REFERENCES parts (id)
    )
    ''')

    # Tabela de despesas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        description TEXT,
        value REAL,
        category TEXT,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()

def insert_sample_data(conn: sqlite3.Connection):
    """Insere dados de exemplo no banco de dados"""
    cursor = conn.cursor()

    # inserir nada

    conn.commit()
