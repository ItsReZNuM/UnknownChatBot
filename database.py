# database.py

import sqlite3
from config import logger, ADMIN_USER_ID

DB_FILE = "users.db"

def init_db():
    """پایگاه داده و جدول کاربران را در صورت عدم وجود ایجاد می‌کند."""
    try:
        # check_same_thread=False برای جلوگیری از خطاهای احتمالی اضافه شد
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def add_user(user_id, username, first_name):
    """یک کاربر جدید را به دیتابیس اضافه می‌کند در صورتی که از قبل وجود نداشته باشد."""
    if user_id == ADMIN_USER_ID:
        return
        
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name) VALUES (?, ?, ?)",
                       (user_id, username if username else "ندارد", first_name))
        conn.commit()
        conn.close()
        logger.info(f"User {user_id} added or already exists.")
    except Exception as e:
        logger.error(f"Error adding user {user_id}: {e}")

def get_all_users():
    """لیستی از آیدی تمام کاربران را برای ارسال پیام همگانی برمی‌گرداند."""
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        conn.close()
        return [user[0] for user in users]
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        return []