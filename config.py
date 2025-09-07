# config.py

import telebot
import os
from logging import getLogger
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
from time import time

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))

bot = telebot.TeleBot(TOKEN)
logger = getLogger(__name__)

blocked_users = set()
message_tracker = {}

bot_start_time = datetime.now(timezone('Asia/Tehran')).timestamp()