import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "bank.db"

# -------------------------
# CONNECT TO DATABASE
# -------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# INIT DATABASE
# -------------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # -------------------------
    # USERS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            account_type TEXT DEFAULT 'savings',
            balance REAL DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )
    """)

    # -------------------------
    # TRANSACTIONS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # -------------------------
    # CARDS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_number TEXT,
            brand TEXT,
            note TEXT,
            expiry TEXT,
            cvv TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()

    # -------------------------
    # CREATE ADMIN USER
    # -------------------------
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    admin = cursor.fetchone()
    if not admin:
        cursor.execute("""
            INSERT INTO users (username, password, name, is_admin)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "Admin",
            1
        ))
        conn.commit()

    # -------------------------
    # CREATE DEMO USER
    # -------------------------
    cursor.execute("SELECT * FROM users WHERE username = ?", ("Salon454@yahoo.com",))
    user = cursor.fetchone()
    if not user:
        cursor.execute("""
            INSERT INTO users (username, password, name, account_type, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Salon454@yahoo.com",
            generate_password_hash("Michele123@"),
            "Salon User",
            "savings",
            126000
        ))
        conn.commit()

        # Get the inserted user id
        cursor.execute("SELECT id FROM users WHERE username = ?", ("Salon454@yahoo.com",))
        user_id = cursor.fetchone()["id"]

        # Add card for this user
        cursor.execute("""
            INSERT INTO cards (user_id, card_number, brand, note, expiry, cvv)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "4532 1890 7765 4432",
            "Visa",
            "Savings Account Card",
            "12/28",
            "247"
        ))
        conn.commit()

    conn.close()

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def get_user(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_accounts(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    account = cursor.fetchall()
    conn.close()
    return account

def get_transactions(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    txns = cursor.fetchall()
    conn.close()
    return txns

def get_cards(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE user_id = ?", (user_id,))
    cards = cursor.fetchall()
    conn.close()
    return cards

def add_demo_user(username, password, name, account_type, balance, card_brand, card_number, card_note):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("""
            INSERT INTO users (username, password, name, account_type, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            generate_password_hash(password),
            name,
            account_type,
            balance
        ))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()["id"]
        cursor.execute("""
            INSERT INTO cards (user_id, card_number, brand, note, expiry, cvv)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            card_number,
            card_brand,
            card_note,
            "12/28",
            "247"
        ))
        conn.commit()
    conn.close()

# -------------------------
# INITIALIZE DB IF RUN DIRECTLY
# -------------------------
if __name__ == "__main__":
    init_db()