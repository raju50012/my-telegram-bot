import os
import telebot
from telebot import types
import sqlite3
from flask import Flask
from threading import Thread

# বটের টোকেন ও গ্রুপ আইডি
API_TOKEN = '8828787421:AAHYwuohqRfc0mqy3VRKWofUKhworwmBO7Y'
bot = telebot.TeleBot(API_TOKEN)

GMAIL_GROUP_ID = -5231446702       
WITHDRAW_GROUP_ID = -5291146876    

# ---- Render-এর জন্য ব্যাকগ্রাউন্ড ওয়েব সার্ভার ----
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ---- ডাটাবেজ সেটআপ ----
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def get_balance(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def update_balance(user_id, amount):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    update_balance(user_id, 0)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 কাজ নিন", "📥 জিমেইল সাবমিট")
    markup.add("💰 ব্যালেন্স চেক", "💸 টাকা তুলুন")
    bot.send_message(message.chat.id, "👋 জিমেইল ক্রিয়েট এবং আর্নিং বটে আপনাকে স্বাগতম!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    if message.text == "🎁 কাজ নিন":
        text = "📝 **আজকের কাজের নিয়ম:**\n• পাসওয়ার্ড স্ট্রং দিবেন।\n• রিকভারি মেইল যুক্ত করবেন।"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    elif message.text == "💰 ব্যালেন্স চেক":
        balance = get_balance(user_id)
        bot.send_message(message.chat.id, f"💵 আপনার বর্তমান ব্যালেন্স: *{balance} টাকা*।", parse_mode="Markdown")
    elif message.text == "📥 জিমেইল সাবমিট":
        msg = bot.send_message(message.chat.id, "📥 ফরম্যাটে লিখে পাঠান:\n`email:password`")
        bot.register_next_step_handler(msg, process_gmail_submission)
    elif message.text == "💸 টাকা তুলুন":
        balance = get_balance(user_id)
        if balance < 100:
            bot.send_message(message.chat.id, f"❌ নূন্যতম ১০০ টাকা লাগবে।")
        else:
            msg = bot.send_message(message.chat.id, f"টাকার পরিমাণ লিখে পাঠান।")
            bot.register_next_step_handler(msg, process_withdraw_request)

def process_gmail_submission(message):
    user_id = message.from_user.id
    text = message.text
    if ":" not in text or "@gmail.com" not in text.lower():
        bot.send_message(message.chat.id, "❌ ভুল ফরম্যাট!")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ কনফার্ম", callback_data=f"approve_{user_id}_{text.split(':')[0]}"),
               types.InlineKeyboardButton("❌ রিজেক্ট", callback_data=f"reject_{user_id}"))
    bot.send_message(GMAIL_GROUP_ID, f"📥 নতুন জিমেইল!\n👤 আইডি: `{user_id}`\n📧 ডাটা: `{text}`", reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ অ্যাডমিনের কাছে পাঠানো হয়েছে।")

def process_withdraw_request(message):
    user_id = message.from_user.id
    payment_details = message.text
    balance = get_balance(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ পেইড", callback_data=f"paid_{user_id}"))
    bot.send_message(WITHDRAW_GROUP_ID, f"💸 উইথড্র!\n👤 আইডি: `{user_id}`\n🏦 তথ্য: {payment_details}", reply_markup=markup)
    bot.send_message(message.chat.id, "🚀 রিকোয়েস্ট জমা হয়েছে।")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    if data.startswith("approve_"):
        worker_id = int(data.split("_")[1])
        update_balance(worker_id, 25)
        bot.send_message(worker_id, f"✅ ২৫ টাকা যোগ করা হয়েছে।")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🟢 কনফার্মড!")
    elif data.startswith("reject_"):
        worker_id = int(data.split("_")[1])
        bot.send_message(worker_id, "❌ বাতিল করা হয়েছে।")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🔴 বাতিল!")
    elif data.startswith("paid_"):
        worker_id = int(data.split("_")[1])
        balance = get_balance(worker_id)
        update_balance(worker_id, -balance)
        bot.send_message(worker_id, "🎉 উইথড্র সফল হয়েছে।")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🟢 পেইড!")

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("বট সফলভাবে চালু হয়েছে...")
    bot.polling(none_stop=True)
