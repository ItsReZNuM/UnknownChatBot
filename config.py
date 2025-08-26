import telebot
import os
from logging import getLogger
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
from time import time

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# خواندن توکن و آیدی ادمین از متغیرهای محیطی
TOKEN = os.getenv("TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))

# ساخت نمونه اصلی ربات
bot = telebot.TeleBot(TOKEN)

# تنظیمات لاگر
logger = getLogger(__name__)

# متغیرهای درون حافظه‌ای (in-memory) برای مدیریت کاربران
blocked_users = set()
message_tracker = {}

# زمان شروع به کار ربات برای فیلتر کردن پیام‌های قدیمی
bot_start_time = datetime.now(timezone('Asia/Tehran')).timestamp()