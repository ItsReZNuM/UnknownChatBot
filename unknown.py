import telebot
from telebot import types
from datetime import datetime
from pytz import timezone
from time import time , sleep
import json
import os
from logging import getLogger
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

blocked_users = set()
bot = telebot.TeleBot(TOKEN)
logger = getLogger(__name__)
message_tracker = {}
user_data = {}
USERS_FILE = "users.json"

commands = [
    telebot.types.BotCommand("start", "شروع ربات"),
]
bot.set_my_commands(commands)

bot_start_time = datetime.now(timezone('Asia/Tehran')).timestamp()

def save_user(user_id, username):
    if user_id == ADMIN_USER_ID:
        return
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to read users.json, starting with empty list")
    
    if not any(user['id'] == user_id for user in users):
        users.append({"id": user_id, "username": username if username else "ندارد"})
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved user {user_id} to users.json")
        except Exception as e:
            logger.error(f"Error saving user {user_id} to users.json: {e}")

def is_message_valid(message):
    message_time = message.date
    logger.info(f"Checking message timestamp: {message_time} vs bot_start_time: {bot_start_time}")
    if message_time < bot_start_time:
        logger.warning(f"Ignoring old message from user {message.chat.id} sent at {message_time}")
        return False
    return True

def check_rate_limit(user_id):
    current_time = time()
    
    if user_id not in message_tracker:
        message_tracker[user_id] = {'count': 0, 'last_time': current_time, 'temp_block_until': 0}
    
    if current_time < message_tracker[user_id]['temp_block_until']:
        remaining = int(message_tracker[user_id]['temp_block_until'] - current_time)
        return False, f"شما به دلیل ارسال پیام زیاد تا {remaining} ثانیه نمی‌تونید پیام بفرستید 😕"
    
    if current_time - message_tracker[user_id]['last_time'] > 1:
        message_tracker[user_id]['count'] = 0
        message_tracker[user_id]['last_time'] = current_time
    
    message_tracker[user_id]['count'] += 1
    
    if message_tracker[user_id]['count'] > 2:
        message_tracker[user_id]['temp_block_until'] = current_time + 30
        return False, "شما بیش از حد پیام فرستادید! تا ۳۰ ثانیه نمی‌تونید پیام بفرستید 😕"
    
    return True, ""

def send_broadcast(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id != ADMIN_USER_ID:
        return
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to read users.json")
            bot.send_message(user_id, "❌ خطا در خواندن لیست کاربران!")
            return
    success_count = 0
    for user in users:
        try:
            bot.send_message(user["id"], message.text)
            success_count += 1
            sleep(0.5)
        except Exception as e:
            logger.warning(f"Failed to send broadcast to user {user['id']}: {e}")
            continue
    bot.send_message(user_id, f"پیام به {success_count} کاربر ارسال شد 📢")
    logger.info(f"Broadcast sent to {success_count} users by admin {user_id}")

@bot.message_handler(commands=['start'])
def start(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    allowed, error_message = check_rate_limit(user_id)
    if not allowed:
        bot.send_message(user_id, error_message)
        return
    save_user(user_id, user_name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if user_id == ADMIN_USER_ID:
        btn_special = types.KeyboardButton("پیام همگانی 📢")
        markup.add(btn_special)

    if user_id == ADMIN_USER_ID:
        bot_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.reply_to(message, f'''
این لینک ناشناس توعه، می‌تونی با دادن این به دوستات، با اونا چت ناشناس داشته باشی\n{bot_link}
'''  , reply_markup = markup)
    else:
        bot.reply_to(message, "سلام به ربات چت ناشناس من خوش اومدی 😊\nهر پیامی که می‌خوای رو بنویس من به دست رضا می‌رسونم😃")

@bot.message_handler(commands=['alive'])
def alive(message):
    bot.reply_to(message, "I'm alive and kicking! 🤖 UnknownBot is here!")

@bot.message_handler(content_types=['text', 'sticker', 'photo', 'video', 'document', 'audio', 'voice', 'animation'])
def handle_message(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    allowed, error_message = check_rate_limit(user_id)
    if not allowed:
        bot.send_message(user_id, error_message)
        return


    if user_id in blocked_users:
        bot.reply_to(message, "هه زهی خیال باطل، فعلا بلاکی برو هر موقع از بلاک دراومدی بیا 😏")
        return

    if user_id == ADMIN_USER_ID:
        if hasattr(message, 'reply_to_message') and message.reply_to_message:
            reply_to_user_id = None
            if message.reply_to_message.forward_from:
                reply_to_user_id = message.reply_to_message.forward_from.id
            elif message.reply_to_message.forward_from_chat:
                reply_to_user_id = message.reply_to_message.forward_from_chat.id

            if reply_to_user_id:
                if message.text:
                    bot.send_message(reply_to_user_id, message.text)
                elif message.sticker:
                    bot.send_sticker(reply_to_user_id, message.sticker.file_id)
                elif message.photo:
                    bot.send_photo(reply_to_user_id, message.photo[-1].file_id)
                elif message.video:
                    bot.send_video(reply_to_user_id, message.video.file_id)
                elif message.document:
                    bot.send_document(reply_to_user_id, message.document.file_id)
                elif message.audio:
                    bot.send_audio(reply_to_user_id, message.audio.file_id)
                elif message.voice:
                    bot.send_voice(reply_to_user_id, message.voice.file_id)
                elif message.animation:
                    bot.send_animation(reply_to_user_id, message.animation.file_id)

                bot.reply_to(message, "پیامت ارسال شد ✅\nصبر کن تا جوابت رو بده")
            else:
                bot.reply_to(message, "خو مرد حسابی من به کی پیام بدم 😑\nاول رو پاسخ یه پیام کلیک کن بعد پیامت")
        else:
            bot.reply_to(message, "خو مرد حسابی من به کی پیام بدم 😑\nاول رو پاسخ یه پیام کلیک کن بعد پیامت")
    else:
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        full_name = f"{first_name} {last_name}" if last_name else first_name

        bot.forward_message(ADMIN_USER_ID, message.chat.id, message.message_id)

        keyboard = types.InlineKeyboardMarkup()
        if user_id in blocked_users:
            keyboard.add(types.InlineKeyboardButton("آن‌بلاک ✅", callback_data=f"unblock_{user_id}"))
        else:
            keyboard.add(types.InlineKeyboardButton("جوابشو بده ✅", callback_data=f"reply_{user_id}"))
            keyboard.add(types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}"))

        bot.send_message(
            ADMIN_USER_ID,
            f"📩 پیام ناشناس جدید:\n"
            f"👤 نام: {full_name}\n"
            f"🆔 آیدی: {user_id}\n"
            f"📧 یوزرنیم: @{username if username else 'ندارد'}\n"
            f"📝 پیام: (فوروارد شده)",
            reply_markup=keyboard
        )

        bot.reply_to(message, "پیامت ارسال شد ✅\nصبر کن تا جوابت رو بده")

@bot.callback_query_handler(func=lambda call: True)
def button_callback(call):
    action, user_id = call.data.split("_")
    user_id = int(user_id)


    if action == "reply":
        bot.set_state(call.from_user.id, 'reply_to_user_id', user_id)

        bot.send_message(
            ADMIN_USER_ID,
            "جوابتو بنویس براش:"
        )

        bot.send_message(user_id, "عه رضا پیامتو دید 🤩\nحالا اگه باهات حال کنه جوابتو میده")

    elif action == "block":
        blocked_users.add(user_id)
        bot.edit_message_text(
            f"کاربر با آیدی {user_id} بلاک شد.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

        bot.send_message(user_id, "خب خب، معلوم نیست چی گفتی یا چکار کردی که از طرف رضا بلاک شدی 😂، حالا دیگه تا موقعی که تو رو از بلاک درنیاره نمی‌تونی بهش پیام بدی")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("آن‌بلاک ✅", callback_data=f"unblock_{user_id}"))
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

    elif action == "unblock":
        blocked_users.discard(user_id)
        bot.edit_message_text(
            f"کاربر با آیدی {user_id} از بلاک خارج شد.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

        bot.send_message(user_id, "خب مثل اینکه بچه خوبی شدی و حالا از بلاک دراومدی و می‌تونی دوباره باهاش صحبت کنی 😊")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("جوابشو بده ✅", callback_data=f"reply_{user_id}"))
        keyboard.add(types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}"))
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

@bot.message_handler(func=lambda message: message.text == "پیام همگانی 📢")
def handle_broadcast(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id != ADMIN_USER_ID:
        bot.send_message(user_id, "این قابلیت فقط برای ادمین‌ها در دسترسه!")
        return
    logger.info(f"Broadcast initiated by admin {user_id}")
    bot.send_message(user_id, "هر پیامی که می‌خوای بنویس تا برای همه کاربران ارسال بشه 📢")
    bot.register_next_step_handler(message, send_broadcast)

def main():
    print("Bot is starting...")
    bot.infinity_polling(none_stop=True)
    print("Bot stopped.")

if __name__ == '__main__':
    main()