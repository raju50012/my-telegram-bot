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
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\n\nWelcome! Select a protocol:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def menu(m):
    uid = m.from_user.id
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    
    if m.text == "🎁 Execute Task":
        gmail = f"task.{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@gmail.com"
        bot.send_message(m.chat.id, f"⚙️ *TASK INITIALIZED*\n\n📧 `{gmail}`\n🔑 `{FIXED_PASSWORD}`\n\n_Submit within 300 seconds._", parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Submit Task", callback_data=f"sub_{gmail}")))
    
    elif m.text == "📊 Intelligence Report":
        d = conn.execute("SELECT balance, tasks_done, level FROM users WHERE user_id=?", (uid,)).fetchone()
        bot.send_message(m.chat.id, f"📊 *INTELLIGENCE DATA*\n\n💰 Capital: {d[0]} BDT\n✅ Completed: {d[1]} Tasks\n🎖 Rank: {d[2]}", parse_mode="Markdown")

    elif m.text == "🚀 Rank System":
        bot.send_message(m.chat.id, "🏅 *CURRENT RANK TIERS*\n\n1. Newbie (0-20 Tasks)\n2. Pro (21-50 Tasks)\n3. Elite (50+ Tasks)", parse_mode="Markdown")

    elif m.text == "💸 Withdraw":
        bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        if bal < 50:
            bot.send_message(m.chat.id, f"⚠️ *Insufficient Capital!*\nYou need at least 50 BDT to withdraw. Current: {bal} BDT.")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⚡ Bkash", callback_data="w_Bkash"),
                       types.InlineKeyboardButton("🚀 Nagad", callback_data="w_Nagad"))
            bot.send_message(m.chat.id, "💳 *Select Payment Method:*", reply_markup=markup, parse_mode="Markdown")
            
    elif m.text == "💬 Support":
        bot.send_message(m.chat.id, f"🌐 *Need Assistance?*\nJoin: {SUPPORT_GROUP_LINK}")

# Callback & Admin Logic
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid =
