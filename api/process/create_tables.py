import sqlite3

CREATE_RIG_TABLE = """
CREATE TABLE IF NOT EXISTS rig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    gpus TEXT,
    hashrate_mh INTEGER,
    power_w INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_BALANCE_TABLE = """
CREATE TABLE IF NOT EXISTS balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_tokens REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

def create_tables(database_name):
    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        # Create the 'rig' table if it doesn't exist
        c.execute(CREATE_RIG_TABLE)

        # Create the 'balance' table if it doesn't exist
        c.execute(CREATE_BALANCE_TABLE)
