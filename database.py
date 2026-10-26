# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match TEXT,
            bet_type TEXT,
            odds REAL,
            result TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

def add_bet(match, bet_type, odds):
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bets (match, bet_type, odds) VALUES (?, ?, ?)",
        (match, bet_type, odds)
    )
    conn.commit()
    bet_id = cursor.lastrowid
    conn.close()
    return bet_id

def update_bet_status(bet_id, status):
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bets SET result = ? WHERE id = ?", (status, bet_id))
    conn.commit()
    conn.close()
