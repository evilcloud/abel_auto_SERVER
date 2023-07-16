import sqlite3
import logging

GET_LATEST_BALANCE = """
SELECT total_tokens, created_at 
FROM balance
ORDER BY created_at DESC 
LIMIT 1
"""


def get_balance(database_name):
    try:
        with sqlite3.connect(database_name) as conn:

            conn.row_factory = sqlite3.Row

            c = conn.cursor()

            c.execute(GET_LATEST_BALANCE)

            row = c.fetchone()

            if row:
                return {
                    "balance": row["total_tokens"],
                    "timestamp": row["created_at"]
                }

            else:
                return {
                    "balance": None,
                    "timestamp": None
                }

    except Exception as e:
        logging.error("Error getting balance: %s", e)
        raise