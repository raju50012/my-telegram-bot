import os, telebot, sqlite3, random, string
from telebot import types
from flask import Flask
from threading import Thread

# Bot Configuration
API_TOKEN = '8828787421:AAE6WlNSj6Bw6I01ZZUv2YyrzQ1s3aid9zg'
bot = telebot.TeleBot(API_TOKEN)
GMAIL_GROUP_ID = -1003929483102       
WITHDRAW_GROUP_ID = -1003951801755
SUPPORT_GROUP_LINK = "https://t.me/suportgrup9228" 
FIXED_PASSWORD = "Blacknoob8"

# Database Setup
def get_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, 
                    balance INTEGER DEFAULT 0, 
                    tasks_done INTEGER DEFAULT 0, 
                    level TEXT DEFAULT 'Newbie')''')
    return conn

# Rank Update Logic
def update_rank(uid):
    conn = get_db()
    t = conn.execute("SELECT tasks_done FROM users WHERE user_id=?", (uid,)).fetchone()[0]
    rank = "Elite" if t > 50 else "Pro" if t > 20 else "Newbie"
    conn.execute("UPDATE users SET level=? WHERE user_id=?", (rank, uid))
    conn.commit()

# Main Menu
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Execute Task", "📊 Intelligence Report", "🚀 Rank System", "💸 Withdraw", "💬 Support")
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\n\nWelcome to the next generation of task automation. Initialize your session:", reply_markup=markup, parse_mode="Markdown")

# Message Handling
@bot.message_handler(func=lambda m: True)
def menu(m):
    uid = m.from_user.id
    if m.text == "🎁 Execute Task":
        gmail = f"task.{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@gmail.com"
        bot.send_message(m.chat.id, f"⚙️ *TASK INITIALIZED*\n\n📧 `{gmail}`\n🔑 `{FIXED_PASSWORD}`\n\n_System Note: Submit within 300 seconds._", parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Submit Task", callback_data=f"sub_{gmail}")))
    
    elif m.text == "📊 Intelligence Report":
        conn = get_db()
        d = conn.execute("SELECT balance, tasks_done, level FROM users WHERE user_id=?", (uid,)).fetchone()
        b, t, l = (d[0], d[1], d[2]) if d else (0, 0, 'Newbie')
        bot.send_message(m.chat.id, f"📊 *INTELLIGENCE DATA*\n\n💰 Capital: {b} BDT\n✅ Completed: {t} Tasks\n🎖 Rank: {l}\n\n_Data synced with central server._", parse_mode="Markdown")

    elif m.text == "🚀 Rank System":
        bot.send_message(m.chat.id, "🏅 *CURRENT RANK TIERS*\n\n1. Newbie (0-20 Tasks)\n2. Pro (21-50 Tasks)\n3. Elite (50+ Tasks)\n\n_Reach Elite to unlock bonuses!_", parse_mode="Markdown")

    elif m.text == "💸 Withdraw":
        conn = get_db()
        bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()
        bal = bal[0] if bal else 0
        if bal < 100:
            bot.send_message(m.chat.id, "⚠️ *Insufficient Capital!* You need at least 100 BDT to initialize withdrawal.")
        else:
            bot.send_message(m.chat.id, "💳 *Select Payment Method:*", reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("⚡ Bkash", callback_data="w_Bkash"),
                types.InlineKeyboardButton("🚀 Nagad", callback_data="w_Nagad")
            ))
            
    elif m.text == "💬 Support":
        bot.send_message(m.chat.id, f"🌐 *Need Assistance?*\n\nJoin our official support group: {SUPPORT_GROUP_LINK}")

# Callback Handling
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("sub_"):
        bot.send_message(GMAIL_GROUP_ID, f"📡 *NEW DATA SUBMISSION*\nUser: `{call.from_user.id}`\nAcc: `{call.data.split('_')[1]}`", parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("VALIDATE & PAY", callback_data=f"app_{call.from_user.id}")))
        bot.answer_callback_query(call.id, "Data processing...")
        
    elif call.data.startswith("app_"):
        uid = int(call.data.split('_')[1])
        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        conn.execute("UPDATE users SET balance = balance + 25, tasks_done = tasks_done + 1 WHERE user_id = ?", (uid,))
        conn.commit()
        update_rank(uid)
        bot.send_message(uid, "✅ *Transaction Success!* Your capital has been updated.")
        bot.edit_message_text("💾 *Task Validated*", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
    elif call.data.startswith("w_"):
        method = call.data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, f"📌 *Enter your {method} Number:*")
        bot.register_next_step_handler(msg, lambda m: (
            bot.send_message(WITHDRAW_GROUP_ID, f"💸 *NEW WITHDRAWAL REQUEST*\nUser: `{call.from_user.id}`\nMethod: {method}\nNumber: `{m.text}`", parse_mode="Markdown"),
            bot.send_message(call.message.chat.id, "✅ *Withdrawal Request Initialized!* Admin will process soon.")
        ))

# Web Server for Deployment
if __name__ == '__main__':
    Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
