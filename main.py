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

# Main Menu (বাংলা ও ইংরেজি মিলিয়ে সাজানো)
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Execute Task", "📊 Intelligence Report", "🚀 Rank System", "💸 Withdraw", "💬 Support")
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\n\nস্বাগতম! আপনার পরবর্তী কাজের জন্য নিচের মেনু থেকে অপশন নির্বাচন করুন:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def menu(m):
    uid = m.from_user.id
    conn = get_db()
    
    # নতুন ইউজারকে ডাটাবেজে যুক্ত করা
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()

    if m.text == "🎁 Execute Task":
        gmail = f"task.{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@gmail.com"
        bot.send_message(m.chat.id, f"⚙️ *TASK INITIALIZED*\n\n📧 `{gmail}`\n🔑 `{FIXED_PASSWORD}`\n\n_৩০০ সেকেন্ডের মধ্যে সাবমিট করুন!_", parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Submit Task", callback_data=f"sub_{gmail}")))
    
    elif m.text == "📊 Intelligence Report":
        d = conn.execute("SELECT balance, tasks_done, level FROM users WHERE user_id=?", (uid,)).fetchone()
        bot.send_message(m.chat.id, f"📊 *আপনার ডাটা রিপোর্ট*\n\n💰 মোট ব্যালেন্স: {d[0]} BDT\n✅ সম্পন্ন কাজ: {d[1]}\n🎖 র‍্যাঙ্ক: {d[2]}", parse_mode="Markdown")

    elif m.text == "💸 Withdraw":
        bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        if bal < 100:
            bot.send_message(m.chat.id, f"⚠️ *ব্যালেন্স কম!*\nউইথড্র করার জন্য কমপক্ষে ১০০ BDT প্রয়োজন। আপনার বর্তমান ব্যালেন্স: {bal} BDT.")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⚡ Bkash", callback_data="w_Bkash"),
                       types.InlineKeyboardButton("🚀 Nagad", callback_data="w_Nagad"))
            bot.send_message(m.chat.id, "💳 *পেমেন্ট মেথড সিলেক্ট করুন:*", reply_markup=markup, parse_mode="Markdown")
            
    elif m.text == "💬 Support":
        bot.send_message(m.chat.id, f"🌐 *সহায়তা প্রয়োজন?*\nআমাদের সাপোর্ট গ্রুপে জয়েন করুন: {SUPPORT_GROUP_LINK}")

# Callback Handling
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("sub_"):
        bot.send_message(GMAIL_GROUP_ID, f"📡 *নতুন সাবমিশন*\nUser: `{call.from_user.id}`\nAcc: `{call.data.split('_')[1]}`", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("VALIDATE & PAY", callback_data=f"app_{call.from_user.id}")))
        bot.answer_callback_query(call.id, "সাবমিশন গ্রহণ করা হয়েছে!")
    
    elif call.data.startswith("app_"):
        target_uid = int(call.data.split('_')[1])
        conn = get_db()
        conn.execute("UPDATE users SET balance = balance + 25, tasks_done = tasks_done + 1 WHERE user_id = ?", (target_uid,))
        conn.commit()
        bot.send_message(target_uid, "✅ *পেমেন্ট সফল!* আপনার ব্যালেন্সে ২৫ টাকা যোগ করা হয়েছে।")
        bot.edit_message_text("💾 *Validated*", call.message.chat.id, call.message.message_id)

    elif call.data.startswith("w_"):
        method = call.data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, f"📌 *আপনার {method} নাম্বারটি লিখুন:*")
        bot.register_next_step_handler(msg, lambda m: (
            bot.send_message(WITHDRAW_GROUP_ID, f"💸 *নতুন উইথড্র রিকোয়েস্ট*\nUser: `{call.from_user.id}`\nMethod: {method}\nNumber: `{m.text}`"),
            bot.send_message(call.message.chat.id, "✅ *উইথড্র রিকোয়েস্ট সফল!* অ্যাডমিন দ্রুত পেমেন্ট চেক করবে।")
        ))

if __name__ == '__main__':
    Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
