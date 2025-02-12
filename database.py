import sqlite3
from datetime import datetime

def init_db():
    with sqlite3.connect('testflight.db') as conn:
        cursor = conn.cursor()
        
        # Create subscriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email, url)
        )
        ''')
        
        # Create status_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            is_accepting BOOLEAN NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()

def add_subscription(email, url):
    try:
        with sqlite3.connect('testflight.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO subscriptions (email, url) VALUES (?, ?)',
                (email, url)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def get_subscriptions(url=None):
    with sqlite3.connect('testflight.db') as conn:
        cursor = conn.cursor()
        if url:
            cursor.execute('SELECT email FROM subscriptions WHERE url = ?', (url,))
            return [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute('SELECT DISTINCT url FROM subscriptions')
            return [row[0] for row in cursor.fetchall()]

def remove_subscriptions(url):
    with sqlite3.connect('testflight.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE url = ?', (url,))
        conn.commit()

def add_status_history(url, is_accepting):
    with sqlite3.connect('testflight.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO status_history (url, is_accepting) VALUES (?, ?)',
            (url, is_accepting)
        )
        conn.commit()