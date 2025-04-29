"""
Handles DB connection, create tables, queries
"""

import sqlite3
from pathlib import Path
from sqlite3 import Connection

DB_PATH = Path(r'X/rma_database/rma.db')


def create_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    return conn


def initialize_database() -> None:
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rmas (
                rma_number TEXT PRIMARY KEY,
                customer TEXT,
                product TEXT,
                department TEXT,
                is_warranty INTEGER,
                serial_number TEXT,
                reason_for_return TEXT,
                purchase_order_number TEXT,
                work_order TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
