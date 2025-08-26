# 😈 AnonExposed: The Not-So-Anonymous Chat Bot

Welcome to **AnonExposed**, the Telegram bot that *used* to be all about anonymous chats... until its mischievous admin decided to spice things up a bit! 😉 Now, while your users think they're sending messages into the void, you, the admin, get to see *exactly* who's behind every "anonymous" message. It's anonymous for them, but a transparent window for you! 👀

## ✨ Features

* **🕵️‍♂️ Reveal Sender Identity:** The core feature! Receive "anonymous" messages with full sender details (Name, User ID, Username) directly in your admin chat. No more guessing games!
* **↩️ Direct Reply:** Reply directly to "anonymous" messages from your admin panel. Your reply goes straight back to the sender, maintaining the illusion of anonymity for them.
* **🚫 User Blocking:** Got a spammer or someone annoying? Block users instantly from your admin interface. They won't be able to bother you anymore!
* **✅ User Unblocking:** Had a change of heart? Unblock users just as easily.
* **📢 Broadcast Messaging (Admin Only):** Send messages to all your bot's users at once. Perfect for announcements or just saying hello!
* **⏱️ Rate Limiting:** Prevents message flooding by users, keeping your chat clean and manageable.
* **💾 User Management:** Automatically saves user IDs and usernames to a JSON file for easy tracking.
* **⏰ Uptime Check:** A simple `/alive` command to check if the bot is running.

## 🚀 How to Use (for Users)

1.  **Start the Bot:** Find the bot on Telegram and hit the "Start" button or send `/start`.
2.  **Send Your Anonymous Message:** Type anything you want and send it. The bot will confirm that your message has been "delivered to Reza" (the admin) and that you should wait for a reply.
3.  **Wait for a Reply:** Your message reaches the admin, who can then choose to reply.

## 👑 How to Use (for the Mischievous Admin)

1.  **Set Your Admin ID:** Make sure your Telegram User ID is correctly listed in the `ADMIN_USER_ID` variable in your bot's Python script.
2.  **Start the Bot:** Run your bot's Python script.
3.  **Receive "Anonymous" Messages:** When a user sends a message, you (the admin) will receive a forwarded message along with a detailed information card showing their name, user ID, and username!
4.  **Reply Directly:** Use the "جوابشو بده ✅" (Reply) button below the message details to send a direct reply to the user.
5.  **Block/Unblock Users:** Use the "بلاکه بلاک ❌" (Block) or "آن‌بلاک ✅" (Unblock) buttons to manage user access.
6.  **Send Broadcasts:** Use the "پیام همگانی 📢" (Broadcast Message) button from your keyboard to send a message to all users.

## 🛠️ Setup & Installation

To get AnonExposed up and running, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ItsReZNuM/UnknownChatBot](https://github.com/ItsReZNuM/UnknownChatBot)
    cd AnonExposed
    ```
2.  **Install Dependencies:**
    Make sure you have `pyTelegramBotAPI` and `pytz` installed.
    ```bash
    pip install pyTelegramBotAPI pytz
    pip install -r requirements.txt
    ```
3.  **Configure Your Bot:**
    * Make an .env file like the example in the repo. 
    * Replace `'YOUR_BOT_TOKEN'` with your actual Telegram Bot Token from BotFather:
        ```python
        TOKEN = 'YOUR_BOT_TOKEN' # Replace with your bot's token
        ```
    * Replace `[YOUR_ADMIN_USER_ID]` with your Telegram User ID (as an integer) in the `ADMIN_USER_ID` list. You can get your User ID by sending `/id` to [@userinfobot](https://t.me/userinfobot) or similar bots.
        ```python
        ADMIN_USER_ID = [YOUR_ADMIN_USER_ID] # Replace with your actual user ID(s)
        ```
4.  **Run the Bot:**
    ```bash
    python main.py
    ```
    Your bot should now be running! 🎉

## 🐛 Troubleshooting

* **"Bad Request: chat not found" Error:** This usually means the bot tried to send a message to a user who has blocked the bot or never started it. The bot cannot send messages to such users.
* **Admin Features Not Showing:** Ensure your `ADMIN_USER_ID` is correctly set in the code and that you are using the correct Telegram account. Also, double-check the comparison logic in your code to ensure `user_id in ADMIN_USER_ID` is used for checking admin status (if you've modified the original code).

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📜 License

This project is open-source.

---
Made with ❤️ by ReZNuM