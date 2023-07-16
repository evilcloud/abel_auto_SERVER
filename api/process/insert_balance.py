import sqlite3
from datetime import datetime

INSERT_BALANCE = """
INSERT INTO balance (total_tokens, created_at)
VALUES (?, ?)  
"""


def insert_balance(balance, timestamp, database_name):
    # Input validation
    if not isinstance(balance, (int, float)):
        raise ValueError('Balance must be a number')

    if balance < 0:
        raise ValueError('Balance cannot be negative')

    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        if timestamp is None:
            now = datetime.now()
            timestamp = now.isoformat(' ')
            c.execute(INSERT_BALANCE, (balance, timestamp))

        else:
            c.execute(INSERT_BALANCE, (balance, timestamp))


def insert_balance_with_timestamp(balance, timestamp, database_name):
    # Input validation
    if not isinstance(balance, (int, float)):
        raise ValueError('Balance must be a number')

    if balance < 0:
        raise ValueError('Balance cannot be negative')

    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        c.execute(INSERT_BALANCE, (balance, timestamp))