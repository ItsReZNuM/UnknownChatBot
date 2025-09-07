# main.py

import telebot
import logging  # ماژول logging رو وارد کن
from config import bot, logger
from database import init_db
import handlers  # وارد کردن این ماژول باعث ثبت شدن تمام هندلرها می‌شود

def main():
    # =============== بخش اضافه شده برای تنظیمات لاگ ===============
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding='utf-8'),  # ذخیره لاگ در فایل
            logging.StreamHandler()  # نمایش لاگ در کنسول
        ]
    )
    # ==========================================================
    
    # تنظیم دستورات ربات
    commands = [
        telebot.types.BotCommand("start", "شروع ربات"),
        telebot.types.BotCommand("alive", "چک کردن وضعیت ربات"),
    ]
    bot.set_my_commands(commands)
    
    # ساخت فایل دیتابیس در صورت عدم وجود
    init_db()
    
    logger.info("Bot is starting...")
    print("Bot is running...")
    
    # شروع به گوش دادن به پیام‌ها
    bot.infinity_polling(none_stop=True)
    
    print("Bot stopped.")

if __name__ == '__main__':
    main()