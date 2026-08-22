"""
User Wallet Ledger
System: Nexus Reseller Core
"""

import sqlite3
from typing import Dict, Any, List, Optional

class WalletLedger:
    def __init__(self, db_path: str = "ghost_reseller_wallet.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance_usdt REAL DEFAULT 0.0,
                    total_spent_usdt REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    amount_usdt REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_or_create_user(self, user_id: int, username: Optional[str] = "") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO users (user_id, username, balance_usdt) VALUES (?, ?, 0.0)", (user_id, username or ""))
                conn.commit()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
            return dict(row)

    def credit_balance(self, user_id: int, amount_usdt: float, description: str = "Deposit") -> float:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance_usdt = balance_usdt + ? WHERE user_id = ?", (amount_usdt, user_id))
            cursor.execute("INSERT INTO transactions (user_id, type, amount_usdt, description) VALUES (?, 'deposit', ?, ?)", (user_id, amount_usdt, description))
            conn.commit()
            cursor.execute("SELECT balance_usdt FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()["balance_usdt"]

    def deduct_balance(self, user_id: int, amount_usdt: float, description: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance_usdt FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row or row["balance_usdt"] < amount_usdt:
                return False
                
            cursor.execute("UPDATE users SET balance_usdt = balance_usdt - ?, total_spent_usdt = total_spent_usdt + ? WHERE user_id = ?", (amount_usdt, amount_usdt, user_id))
            cursor.execute("INSERT INTO transactions (user_id, type, amount_usdt, description) VALUES (?, 'purchase', ?, ?)", (user_id, amount_usdt, description))
            conn.commit()
            return True
