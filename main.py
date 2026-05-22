import os, telebot, sqlite3, random, string
from telebot import types
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
API_TOKEN = '8828787421:AAE6WlNSj6Bw6I01ZZUv2YyrzQ1s3aid9zg'
bot = telebot.TeleBot(API_TOKEN)
GMAIL_GROUP_ID = -1003929483102       
WITHDRAW_GROUP_ID = -1003951801755 
SUPPORT_GROUP_LINK = "https://t.me/suportgrup9228" 
FIXED_PASSWORD = "Blacknoob8"

# গ্লোবাল রেট ভেরিয়েবল
task_rate = 15 

# --- ডাটাবেজ ---
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

# --- মেইন মেনু ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Execute Task", "📊 Intelligence Report", "🚀 Rank System", "💸 Withdraw", "💬 Support")
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\n\nMainframe ready. Select a protocol:", reply_markup=markup, parse_mode="Markdown")

# --- মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda m: True)
def menu(m):
    global task_rate
    uid = m.from_user.id
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    
    # গ্রুপ নোটিশ ও রেট কন্ট্রোল হ্যান্ডলার
    if m.chat.id == WITHDRAW_GROUP_ID and m.text:
        if m.text.startswith('/rate '):
            try:
                task_rate = int(m.text.split(' ')[1])
                bot.reply_to(m, f"✅ কাজের রেট সফলভাবে {task_rate} টাকা করা হয়েছে।")
            except:
                bot.reply_to(m, "❌ ভুল ফরম্যাট! সঠিক নিয়ম: `/rate 20`")
            return
        elif not m.text.startswith('/'):
            users = conn.execute("SELECT user_id FROM users").fetchall()
            for user in users:
                try: bot.send_message(user[0], f"📢 *অফিসিয়াল নোটিশ:*\n\n{m.text}", parse_mode="Markdown")
                except: pass
            bot.reply_to(m, "✅ নোটিশ পাঠানো হয়েছে।")
            return

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
            markup.add(types.InlineKeyboardButton("⚡ Bkash", callback_data="w_Bkash"), types.InlineKeyboardButton("🚀 Nagad", callback_data="w_Nagad"))
            bot.send_message(m.chat.id, "💳 *Select Payment Method:*\n\n_Minimum withdrawal: 50 BDT_", reply_markup=markup, parse_mode="Markdown")
            
    elif m.text == "💬 Support":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 Join Support Group", url=SUPPORT_GROUP_LINK))
        bot.send_message(m.chat.id, "🌐 *TECHNICAL SUPPORT CENTER*", reply_markup=markup, parse_mode="Markdown")

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global task_rate
    uid = call.from_user.id
    conn = get_db()
    
    if call.data.startswith("sub_"):
        d = conn.execute("SELECT balance, tasks_done, level FROM users WHERE user_id=?", (uid,)).fetchone()
        bot.send_message(GMAIL_GROUP_ID, f"📡 *NEW DATA SUBMISSION*\n\n👤 User: `{uid}`\n💰 Bal: {d[0]}\n✅ Tasks: {d[1]}\n📧 Acc: `{call.data.split('_')[1]}`", 
        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ SUCCESS", callback_data=f"app_{uid}"), types.InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{uid}")), parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ Submission Successful!")

    elif call.data.startswith("app_"):
        t_uid = int(call.data.split('_')[1])
        conn.execute("UPDATE users SET balance = balance + ?, tasks_done = tasks_done + 1 WHERE user_id = ?", (task_rate, t_uid))
        conn.commit()
        update_rank(t_uid)
        bot.send_message(t_uid, f"✅ *Transaction Success!* {task_rate} BDT added.")
        bot.edit_message_text(f"💾 *Task Validated ({task_rate} BDT)*", call.message.chat.id, call.message.message_id)

    elif call.data.startswith("w_"):
        method = call.data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, f"📌 *Enter your {method} Number:*")
        bot.register_next_step_handler(msg, lambda m: (
            bot.send_message(WITHDRAW_GROUP_ID, f"💸 *NEW WITHDRAWAL REQUEST*\n\n👤 User: `{uid}`\n💳 Method: {method}\n📱 Number: `{m.text}`", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ পেমেন্ট করেছি", callback_data=f"paid_{uid}")), parse_mode="Markdown"),
            bot.send_message(call.message.chat.id, "✅ *Request Initialized!* Admin will process soon.")
        ))

    elif call.data.startswith("paid_"):
        t_uid = int(call.data.split('_')[1])
        conn.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (t_uid,))
        conn.commit()
        bot.send_message(t_uid, "🎉 *অভিনন্দন!* আপনার পেমেন্ট সফল হয়েছে।")
        bot.edit_message_text("✅ *পেমেন্ট সম্পন্ন*", call.message.chat.id, call.message.message_id)

if __name__ == '__main__':
    Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
