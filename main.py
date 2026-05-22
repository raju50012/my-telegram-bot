import os, telebot, sqlite3, random, string
from telebot import types
from flask import Flask
from threading import Thread

# --- Configuration ---
API_TOKEN = '8828787421:AAE6WlNSj6Bw6I01ZZUv2YyrzQ1s3aid9zg'
bot = telebot.TeleBot(API_TOKEN)
GMAIL_GROUP_ID = -1003929483102       
WITHDRAW_GROUP_ID = -1003951801755
SUPPORT_GROUP_LINK = "https://t.me/suportgrup9228" 
FIXED_PASSWORD = "Blacknoob8"

# --- Database ---
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

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Execute Task", "📊 Intelligence Report", "🚀 Rank System", "💸 Withdraw", "💬 Support")
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\n\nMainframe ready.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def menu(m):
    uid = m.from_user.id
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    
    if m.text == "🎁 Execute Task":
        gmail = f"task.{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@gmail.com"
        bot.send_message(m.chat.id, f"⚙️ *TASK*\n📧 `{gmail}`\n🔑 `{FIXED_PASSWORD}`", parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Submit Task", callback_data=f"sub_{gmail}")))
    
    elif m.text == "📊 Intelligence Report":
        d = conn.execute("SELECT balance, tasks_done, level FROM users WHERE user_id=?", (uid,)).fetchone()
        bot.send_message(m.chat.id, f"📊 *REPORT*\n💰 Balance: {d[0]} BDT\n✅ Tasks: {d[1]}\n🎖 Rank: {d[2]}", parse_mode="Markdown")

    elif m.text == "🚀 Rank System":
        bot.send_message(m.chat.id, "🏅 *RANKS*\nNewbie: 0-20\nPro: 21-50\nElite: 50+", parse_mode="Markdown")

    elif m.text == "💸 Withdraw":
        bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        if bal < 50:
            bot.send_message(m.chat.id, f"⚠️ *Low Balance*\nMinimum 50 BDT required. Current: {bal} BDT.")
        else:
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⚡ Bkash", callback_data="w_Bkash"), types.InlineKeyboardButton("🚀 Nagad", callback_data="w_Nagad"))
            bot.send_message(m.chat.id, "💳 *Select Method:*", reply_markup=markup, parse_mode="Markdown")
            
    elif m.text == "💬 Support":
        bot.send_message(m.chat.id, f"🌐 *Link:* {SUPPORT_GROUP_LINK}")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    if call.data.startswith("sub_"):
        bot.send_message(GMAIL_GROUP_ID, f"📡 *NEW SUBMISSION*\nUser: `{uid}`\nAcc: `{call.data.split('_')[1]}`", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ SUCCESS", callback_data=f"app_{uid}"), types.InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{uid}")))
    elif call.data.startswith("app_"):
        t_uid = int(call.data.split('_')[1])
        get_db().execute("UPDATE users SET balance = balance + 15, tasks_done = tasks_done + 1 WHERE user_id = ?", (t_uid,))
        get_db().commit()
        update_rank(t_uid)
        bot.send_message(t_uid, "✅ *Payment Successful!* 15 BDT added.")
        bot.edit_message_text("💾 *Validated*", call.message.chat.id, call.message.message_id)
    elif call.data.startswith("rej_"):
        bot.send_message(int(call.data.split('_')[1]), "⚠️ *Rejected.*")
        bot.edit_message_text("❌ *Rejected*", call.message.chat.id, call.message.message_id)
    elif call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, f"📌 *Enter your {call.data.split('_')[1]} Number:*")
        bot.register_next_step_handler(call.message, lambda m: bot.send_message(WITHDRAW_GROUP_ID, f"💸 *WITHDRAW*\nUser: `{uid}`\nNum: `{m.text}`"))

if __name__ == '__main__':
    Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
