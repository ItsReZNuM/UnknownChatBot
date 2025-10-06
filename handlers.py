# handlers.py

from telebot import types
from telebot.types import ForceReply
from time import sleep

from config import bot, ADMIN_USER_ID, logger, blocked_users
from utils import is_message_valid, check_rate_limit
from database import add_user, get_all_users

# --- تابع کمکی برای ارسال پاسخ ادمین ---

def send_reply_to_user(message, target_user_id):
    """پیام ادمین را به کاربر مورد نظر ارسال می‌کند."""
    try:
        bot.copy_message(target_user_id, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ پیام شما با موفقیت ارسال شد.")
    except Exception as e:
        logger.error(f"Failed to send admin reply to user {target_user_id}: {e}")
        bot.send_message(message.chat.id, f"❌ ارسال پیام با خطا مواجه شد: {e}")

# --- هندلرهای دستورات ---

@bot.message_handler(commands=['start'])
def start(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    add_user(user_id, username, user_name)

    if user_id == ADMIN_USER_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("پیام همگانی 📢"))
        bot.reply_to(message, "سلام ادمین عزیز! خوش آمدید.", reply_markup=markup)
    else:
        bot.reply_to(message, "سلام به ربات چت ناشناس من خوش اومدی 😊\nهر پیامی که می‌خوای رو بنویس من به دست رضا می‌رسونم😃")

@bot.message_handler(commands=['alive'])
def alive(message):
    bot.reply_to(message, "I'm alive and kicking! 🤖")

# --- هندلرهای پیام همگانی ---

def send_broadcast(message):
    """پیام ادمین را برای تمام کاربران ارسال می‌کند."""
    if message.chat.id != ADMIN_USER_ID:
        return
        
    user_ids = get_all_users()
    if not user_ids:
        bot.send_message(message.chat.id, "❌ هیچ کاربری در دیتابیس برای ارسال پیام وجود ندارد!")
        return
        
    success_count = 0
    for uid in user_ids:
        try:
            bot.copy_message(uid, message.chat.id, message.message_id)
            success_count += 1
            sleep(0.1)  # تاخیر کم برای جلوگیری از بلاک شدن
        except Exception as e:
            logger.warning(f"Failed to send broadcast to user {uid}: {e}")
            
    bot.send_message(message.chat.id, f"📢 پیام به {success_count} کاربر ارسال شد.")
    logger.info(f"Broadcast sent to {success_count} users by admin {message.chat.id}")

@bot.message_handler(func=lambda message: getattr(message, 'text', None) == "پیام همگانی 📢" and message.chat.id == ADMIN_USER_ID)
def handle_broadcast_button(message):
    """بعد از زدن دکمه پیام همگانی، منتظر پیام ادمین می‌ماند."""
    bot.send_message(message.chat.id, "پیام خود را برای ارسال به همه کاربران بنویسید (متن، عکس و...):")
    bot.register_next_step_handler(message, send_broadcast)

# --- هندلر اصلی پیام‌های کاربران ---

@bot.message_handler(content_types=['text', 'sticker', 'photo', 'video', 'document', 'audio', 'voice', 'animation'])
def handle_user_messages(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id

    # این هندلر فقط برای کاربران عادی است. پیام‌های ادمین توسط هندلرهای دیگر مدیریت می‌شوند.
    if user_id == ADMIN_USER_ID:
        return

    allowed, error_message = check_rate_limit(user_id)
    if not allowed:
        bot.send_message(user_id, error_message)
        return

    if user_id in blocked_users:
        bot.reply_to(message, "هه زهی خیال باطل، فعلا بلاکی برو هر موقع از بلاک دراومدی بیا 😏")
        return

    # ارسال پیام کاربر به ادمین همراه با دکمه‌های جدید
    bot.forward_message(ADMIN_USER_ID, user_id, message.message_id)

    username = message.from_user.username
    keyboard = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton("پاسخ ✍️", callback_data=f"reply_{user_id}")
    block_button = types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}")
    keyboard.add(reply_button, block_button)

    full_name = message.from_user.first_name + (f" {message.from_user.last_name}" if message.from_user.last_name else "")
    bot.send_message(
        ADMIN_USER_ID,
        f"📩 پیام ناشناس جدید از:\n"
        f"👤 نام: {full_name}\n"
        f"🆔 آیدی عددی: {user_id}\n"
        f"👤 یوزرنیم: @{username}" ,
        reply_markup=keyboard,
    )
    bot.reply_to(message, "پیامت ارسال شد ✅\nصبر کن تا جوابت رو بده")

# --- هندلر دکمه‌های شیشه‌ای (Callback) ---

@bot.callback_query_handler(func=lambda call: True)
def button_callback(call):
    try:
        action, user_id_str = call.data.split("_")
        user_id = int(user_id_str)
    except ValueError:
        logger.error(f"Invalid callback data received: {call.data}")
        return

    if action == "reply":
        bot.answer_callback_query(call.id)
        markup = ForceReply(selective=True)
        msg = bot.send_message(
            call.message.chat.id,
            f"پیام خود را برای ارسال به کاربر `{user_id}` بنویسید:",
            reply_markup=markup,
            parse_mode="MarkdownV2"
        )
        bot.register_next_step_handler(msg, send_reply_to_user, user_id)

    elif action == "block":
        blocked_users.add(user_id)
        bot.answer_callback_query(call.id, f"کاربر {user_id} بلاک شد.")
        bot.send_message(user_id, "خب خب، معلوم نیست چی گفتی یا چکار کردی که از طرف رضا بلاک شدی 😂")
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("آن‌بلاک ✅", callback_data=f"unblock_{user_id}"))
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

    elif action == "unblock":
        if user_id in blocked_users:
            blocked_users.remove(user_id)
        bot.answer_callback_query(call.id, f"کاربر {user_id} آن‌بلاک شد.")
        bot.send_message(user_id, "خب مثل اینکه بچه خوبی شدی و حالا از بلاک دراومدی و می‌تونی دوباره باهاش صحبت کنی 😊")

        keyboard = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton("پاسخ ✍️", callback_data=f"reply_{user_id}")
        block_button = types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}")
        keyboard.add(reply_button, block_button)
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )