# handlers.py

from telebot import types
from time import sleep

# forward_mappings رو از کانفیگ وارد می‌کنیم
from config import bot, ADMIN_USER_ID, logger, blocked_users, forward_mappings
from utils import is_message_valid, check_rate_limit
from database import add_user, get_all_users

# --- Command Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    allowed, error_message = check_rate_limit(user_id)
    if not allowed:
        bot.send_message(user_id, error_message)
        return
    
    add_user(user_id, username, user_name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if user_id == ADMIN_USER_ID:
        btn_special = types.KeyboardButton("پیام همگانی 📢")
        markup.add(btn_special)
        bot_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.reply_to(message, f'''
این لینک ناشناس توعه، می‌تونی با دادن این به دوستات، با اونا چت ناشناس داشته باشی\n{bot_link}
'''  , reply_markup = markup)
    else:
        bot.reply_to(message, "سلام به ربات چت ناشناس من خوش اومدی 😊\nهر پیامی که می‌خوای رو بنویس من به دست رضا می‌رسونم😃")

@bot.message_handler(commands=['alive'])
def alive(message):
    bot.reply_to(message, "I'm alive and kicking! 🤖 UnknownBot is here!")

# --- Message Handlers ---

def send_broadcast(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id != ADMIN_USER_ID:
        return
        
    user_ids = get_all_users()
    if not user_ids:
        bot.send_message(user_id, "❌ هیچ کاربری در دیتابیس برای ارسال پیام وجود ندارد!")
        return
        
    success_count = 0
    for uid in user_ids:
        try:
            bot.copy_message(uid, message.chat.id, message.message_id)
            success_count += 1
            sleep(0.5)
        except Exception as e:
            logger.warning(f"Failed to send broadcast to user {uid}: {e}")
            continue
    bot.send_message(user_id, f"پیام به {success_count} کاربر ارسال شد 📢")
    logger.info(f"Broadcast sent to {success_count} users by admin {user_id}")

@bot.message_handler(func=lambda message: message.text == "پیام همگانی 📢" and message.chat.id == ADMIN_USER_ID)
def handle_broadcast_button(message):
    if not is_message_valid(message):
        return
    logger.info(f"Broadcast initiated by admin {message.chat.id}")
    bot.send_message(message.chat.id, "هر پیامی که می‌خوای بنویس تا برای همه کاربران ارسال بشه 📢 (متن، عکس، استیکر و...)")
    bot.register_next_step_handler(message, send_broadcast)


@bot.message_handler(content_types=['text', 'sticker', 'photo', 'video', 'document', 'audio', 'voice', 'animation'])
def handle_all_messages(message):
    if not is_message_valid(message):
        return
    
    user_id = message.from_user.id
    allowed, error_message = check_rate_limit(user_id)
    if not allowed:
        bot.send_message(user_id, error_message)
        return

    if user_id in blocked_users:
        bot.reply_to(message, "هه زهی خیال باطل، فعلا بلاکی برو هر موقع از بلاک دراومدی بیا 😏")
        return

    # =============== بخش ویرایش شده برای ادمین ===============
    if user_id == ADMIN_USER_ID:
        # چک می‌کنیم آیا این پیام، ریپلای است؟
        if message.reply_to_message:
            original_msg_id = message.reply_to_message.message_id
            
            # از دیکشنری که ساختیم، آیدی کاربر رو پیدا می‌کنیم
            reply_to_user_id = forward_mappings.get(original_msg_id)

            if reply_to_user_id:
                try:
                    bot.copy_message(reply_to_user_id, message.chat.id, message.message_id)
                    bot.reply_to(message, "پیامت ارسال شد ✅\nصبر کن تا جوابت رو بده")
                    # بعد از ارسال موفق، این نگاشت رو حذف می‌کنیم تا حافظه پر نشه
                    del forward_mappings[original_msg_id]
                except Exception as e:
                    bot.reply_to(message, f"ارسال پیام با خطا مواجه شد: {e}")
                    logger.error(f"Failed to reply to user {reply_to_user_id}: {e}")
            else:
                # اگر پیام در نگاشت نبود (مثلا پیام قدیمی بوده یا ربات ری‌استارت شده)
                if message.text != "پیام همگانی 📢":
                    bot.reply_to(message, "برای پاسخ به کاربر، باید روی پیام فوروارد شده او ریپلای کنی (ممکنه این پیام قدیمی باشه).")
        else:
            # اگر پیام ادمین ریپلای نبود
            if message.text != "پیام همگانی 📢":
                bot.reply_to(message, "برای پاسخ به کاربر، باید روی پیام فوروارد شده او ریپلای کنی.")

    # =============== بخش ویرایش شده برای کاربران عادی ===============
    else:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += " " + message.from_user.last_name

        # پیام کاربر رو فوروارد می‌کنیم و اطلاعات پیام جدید رو می‌گیریم
        forwarded_msg = bot.forward_message(ADMIN_USER_ID, message.chat.id, message.message_id)
        
        # آیدی پیام فوروارد شده رو به آیدی کاربر اصلی مرتبط می‌کنیم
        forward_mappings[forwarded_msg.message_id] = user_id
        logger.info(f"Mapping created: {forwarded_msg.message_id} -> {user_id}")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}"))

        bot.send_message(
            ADMIN_USER_ID,
            f"📩 پیام ناشناس جدید:\n"
            f"👤 نام: {full_name}\n"
            f"🆔 آیدی: `{user_id}`\n"
            f"📧 یوزرنیم: @{message.from_user.username if message.from_user.username else 'ندارد'}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        bot.reply_to(message, "پیامت ارسال شد ✅\nصبر کن تا جوابت رو بده")

# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda call: True)
def button_callback(call):
    action, user_id_str = call.data.split("_")
    user_id = int(user_id_str)

    if action == "block":
        blocked_users.add(user_id)
        bot.answer_callback_query(call.id, f"کاربر {user_id} بلاک شد.")
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
        bot.answer_callback_query(call.id, f"کاربر {user_id} آن‌بلاک شد.")
        bot.send_message(user_id, "خب مثل اینکه بچه خوبی شدی و حالا از بلاک دراومدی و می‌تونی دوباره باهاش صحبت کنی 😊")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}"))

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )