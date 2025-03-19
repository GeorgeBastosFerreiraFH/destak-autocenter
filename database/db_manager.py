import sqlite3
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import config

logger = logging.getLogger(config.APP_NAME)

class DatabaseManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def initialize(self):
        initialize_database()

    def close(self):
        self.conn.close()

def dict_factory(cursor, row):
    """Converte as linhas do SQLite para dicionários"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = dict_factory
    return conn

def initialize_database():
    """Cria as tabelas se não existirem e insere dados de exemplo"""
    logger.info("Inicializando banco de dados...")

    conn = get_connection()
    cursor = conn.cursor()

    # Criação das tabelas
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

    # Verificar se já existem dados
    cursor.execute("SELECT COUNT(*) as count FROM clients")
    count = cursor.fetchone()['count']

    # Inserir dados de exemplo se o banco estiver vazio
    if count == 0:
        logger.info("Inserindo dados de exemplo...")
        insert_sample_data(conn)

    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado com sucesso!")

def insert_sample_data(conn):
    """Insere dados de exemplo no banco de dados"""
    cursor = conn.cursor()

    # Inserir clientes de exemplo
    cursor.execute('''
    INSERT INTO clients (name, document, address, phone, email)
    VALUES (?, ?, ?, ?, ?)
    ''', ("João Silva", "123.456.789-00", "Rua A, 123", "(11) 98765-4321", "joao@example.com"))

    cursor.execute('''
    INSERT INTO clients (name, document, address, phone, email)
    VALUES (?, ?, ?, ?, ?)
    ''', ("Maria Oliveira", "987.654.321-00", "Av. B, 456", "(11) 91234-5678", "maria@example.com"))

    # Inserir funcionários de exemplo
    cursor.execute('''
    INSERT INTO employees (name, document, role, hire_date)
    VALUES (?, ?, ?, ?)
    ''', ("Carlos Mecânico", "111.222.333-44", "Mecânico", "2020-01-15"))

    cursor.execute('''
    INSERT INTO employees (name, document, role, hire_date)
    VALUES (?, ?, ?, ?)
    ''', ("Ana Atendente", "555.666.777-88", "Atendente", "2021-05-10"))

    # Inserir veículos de exemplo
    cursor.execute('''
    INSERT INTO vehicles (plate, brand, model, year, color, client_id, brand_code, model_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("ABC-1234", "Toyota", "Corolla", 2019, "Prata", 1, "59", "4828"))

    cursor.execute('''
    INSERT INTO vehicles (plate, brand, model, year, color, client_id, brand_code, model_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("XYZ-9876", "Honda", "Civic", 2020, "Preto", 2, "25", "1193"))

    # Inserir peças de exemplo
    cursor.execute('''
    INSERT INTO parts (code, description, stock_quantity, buy_price, sell_price)
    VALUES (?, ?, ?, ?, ?)
    ''', ("P001", "Filtro de Óleo", 15, 25.0, 45.0))

    cursor.execute('''
    INSERT INTO parts (code, description, stock_quantity, buy_price, sell_price)
    VALUES (?, ?, ?, ?, ?)
    ''', ("P002", "Pastilha de Freio", 8, 120.0, 180.0))

    cursor.execute('''
    INSERT INTO parts (code, description, stock_quantity, buy_price, sell_price)
    VALUES (?, ?, ?, ?, ?)
    ''', ("P003", "Óleo de Motor", 20, 90.0, 120.0))

    # Inserir gastos de exemplo
    cursor.execute('''
    INSERT INTO expenses (date, description, value, category, payment_method)
    VALUES (?, ?, ?, ?, ?)
    ''', ("2023-01-15", "Compra de ferramentas", 500.0, "ferramentas", "cartão"))

    cursor.execute('''
    INSERT INTO expenses (date, description, value, category, payment_method)
    VALUES (?, ?, ?, ?, ?)
    ''', ("2023-02-10", "Aluguel da oficina", 2000.0, "aluguel", "boleto"))

    # Inserir ordens de serviço de exemplo
    cursor.execute('''
    INSERT INTO service_orders (number, open_date, vehicle_id, description, status, employee_id, completion_date, total_value, payment_method)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("OS-001", "2023-03-10 10:00:00", 1, "Troca de óleo e filtros", "concluído", 1, "2023-03-11 15:30:00", 250.0, "cartão"))

    cursor.execute('''
    INSERT INTO service_orders (number, open_date, vehicle_id, description, status, employee_id, total_value, payment_method)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("OS-002", "2023-04-05 09:15:00", 2, "Revisão completa", "em andamento", 1, 450.0, "pix"))

    # Inserir relação entre ordens e peças
    cursor.execute('''
    INSERT INTO order_parts (order_id, part_id, quantity, price)
    VALUES (?, ?, ?, ?)
    ''', (1, 1, 1, 45.0))

    cursor.execute('''
    INSERT INTO order_parts (order_id, part_id, quantity, price)
    VALUES (?, ?, ?, ?)
    ''', (1, 3, 1, 120.0))
