import sqlite3
import os
from config import logger, ADMIN_USER_ID

DB_FILE = "users.db"

def init_db():
    """پایگاه داده و جدول کاربران را در صورت عدم وجود ایجاد می‌کند."""
    try:
        conn = sqlite3.connect(DB_FILE)
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # INSERT OR IGNORE فقط در صورتی کاربر را اضافه می‌کند که آیدی او از قبل در جدول نباشد
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()  # نتیجه به صورت لیستی از تاپل‌ها خواهد بود -> [(123,), (456,)]
        conn.close()
        return [user[0] for user in users] # استخراج آیدی از تاپل
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        return []