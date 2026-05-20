import os
import telebot
from telebot import types
import sqlite3
import random
import string
from flask import Flask
from threading import Thread

# বটের রিসেট করা ফ্রেশ টোকেন
API_TOKEN = '8828787421:AAE6WlNSj6Bw6I01ZZUv2YyrzQ1s3aid9zg'
bot = telebot.TeleBot(API_TOKEN)

# 🟢 আপনার আসল গ্রুপ আইডি এবং চ্যাট লিংক এখানে সেট করা হয়েছে ভাই
GMAIL_GROUP_ID = -1003929483102       
WITHDRAW_GROUP_ID = -1003951801755    
SUPPORT_GROUP_LINK = "https://t.me/suportgrup12" 

# সবার জন্য ফিক্সড পাসওয়ার্ড
FIXED_PASSWORD = "Blacknoob8"

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

# ---- ইউনিক জিমেইল জেনারেটর ----
def generate_gmail_task():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    gmail = f"task.user{random_str}@gmail.com"
    return gmail

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    update_balance(user_id, 0)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 কাজ নিন", "💰 ব্যালেন্স চেক")
    markup.add("💸 টাকা তুলুন", "💬 হেল্প গ্রুপ")
    bot.send_message(message.chat.id, "👋 জিমেইল ক্রিয়েট এবং আর্নিং বটে আপনাকে স্বাগতম!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    
    if message.text == "🎁 কাজ নিন":
        gmail = generate_gmail_task()
        
        text = f"📝 **আপনার জন্য নতুন কাজের তথ্য:**\n\n" \
               f"📧 **জিমেইল:** `{gmail}`\n" \
               f"🔑 **পাসওয়ার্ড:** `{FIXED_PASSWORD}`\n\n" \
               f"⚠️ **নির্দেশনা:** ওপরের জিমেইল এবং ফিক্সড পাসওয়ার্ডটি হুবху ব্যবহার করে অ্যাকাউন্টটি তৈরি করুন। তৈরি করা হয়ে গেলে নিচের বাটনে ক্লিক করে সাবমিট করুন।"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ অ্যাকাউন্ট খোলা শেষ (সাবমিট করুন)", callback_data=f"user_submit_{gmail}"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif message.text == "💰 ব্যালেন্স চেক":
        balance = get_balance(user_id)
        bot.send_message(message.chat.id, f"💵 আপনার বর্তমান ব্যালেন্স: *{balance} টাকা*।", parse_mode="Markdown")
        
    elif message.text == "💸 টাকা তুলুন":
        balance = get_balance(user_id)
        if balance < 100:
            bot.send_message(message.chat.id, f"❌ দুঃখিত, আপনার ব্যালেন্স {balance} টাকা। নূন্যতম ১০০ টাকা হলে টাকা তুলতে পারবেন।")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📱 বিকাশ (Bkash)", callback_data="w_method_বিকাশ"),
                       types.InlineKeyboardButton("📱 নগদ (Nagad)", callback_data="w_method_নগদ"))
            bot.send_message(message.chat.id, "💡 টাকা তোলার জন্য নিচের যেকোনো একটি মাধ্যম সিলেক্ট করুন:", reply_markup=markup)
            
    elif message.text == "💬 হেল্প গ্রুপ":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👥 গ্রুপে জয়েন করুন", url=SUPPORT_GROUP_LINK))
        bot.send_message(message.chat.id, "💬 আমাদের পাবলিক ডিসকাশন গ্রুপে জয়েন করতে নিচের বাটনে ক্লিক করুন। এখানে সবাই কথা বলতে পারবে:", reply_markup=markup)

# ---- উইথড্র প্রসেসের পরবর্তী ধাপগুলো ----
def get_withdraw_amount(message, method):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    
    try:
        amount = int(message.text)
        if amount < 100:
            bot.send_message(message.chat.id, "❌ নূন্যতম ১০০ টাকা সাবমিট করতে হবে। আবার চেষ্টা করুন।")
            return
        if amount > balance:
            bot.send_message(message.chat.id, f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! আপনার বর্তমান ব্যালেন্স: {balance} টাকা।")
            return
            
        msg = bot.send_message(message.chat.id, f"✅ পরিমাণ: {amount} টাকা।\n\nএবার আপনার **{method} পার্সোনাল নাম্বারটি** লিখে পাঠান:")
        bot.register_next_step_handler(msg, process_final_withdraw, method, amount)
    except ValueError:
        bot.send_message(message.chat.id, "❌ দয়া করে শুধু সংখ্যায় টাকার পরিমাণটি লিখুন (যেমন: 150)। আবার নতুন করে চেষ্টা করুন।")

def process_final_withdraw(message, method, amount):
    user_id = message.from_user.id
    number = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ পেইড (টাকা পাঠানো শেষ)", callback_data=f"paid_{user_id}_{amount}"))
    
    try:
        bot.send_message(WITHDRAW_GROUP_ID, f"💸 **নতুন উইথড্র রিকোয়েস্ট!**\n\n👤 ইউজার আইডি: `{user_id}`\n🏦 মাধ্যম: *{method}*\n💰 পরিমাণ: *{amount} টাকা*\n📱 নাম্বার: `{number}`\n\nটাকা পাঠানো শেষ হলে নিচের বাটনে ক্লিক করুন।", reply_markup=markup, parse_mode="Markdown")
        bot.send_message(message.chat.id, f"🚀 আপনার {amount} টাকার উইথড্র রিকোয়েস্টটি সফলভাবে জমা হয়েছে। অ্যাডমিন চেক করে আপনার {method} নাম্বারে টাকা পাঠিয়ে দেবে।")
    except:
        bot.send_message(message.chat.id, "❌ উইথড্র গ্রুপ সেটিংস জনিত সমস্যা!")

# ---- বোবাম ক্লিকের ব্যাকএন্ড হ্যান্ডলার ----
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    
    if data.startswith("w_method_"):
        method = data.split("_")[2]
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        msg = bot.send_message(call.message.chat.id, f"🎯 আপনি **{method}** সিলেক্ট করেছেন।\n\nআপনি কত টাকা তুলতে চান তা সংখ্যায় লিখে পাঠান (যেমন: ১০০):")
        bot.register_next_step_handler(msg, get_withdraw_amount, method)

    elif data.startswith("user_submit_"):
        parts = data.split("_")
        gmail = parts[2]
        worker_id = call.from_user.id
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"📧 **জিমেইল:** `{gmail}`\n🔑 **পাসওয়ার্ড:** `{FIXED_PASSWORD}`\n\n⏳ **স্ট্যাটাস:** পেন্ডিং... (অ্যাডমিন চেক করছে, দয়া করে অপেক্ষা করুন)", parse_mode="Markdown")
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("✅ কনফার্ম (লগইন হয়েছে)", callback_data=f"admin_approve_{worker_id}_{gmail}"),
                         types.InlineKeyboardButton("❌ রিজেক্ট (লগইন না হলে)", callback_data=f"admin_reject_{worker_id}_{gmail}"))
        
        try:
            bot.send_message(GMAIL_GROUP_ID, f"📥 **নতুন জিমেইল সাবমিট হয়েছে!**\n👤 ইউজার আইডি: `{worker_id}`\n📧 জিমেইল: `{gmail}`\n🔑 পাসওয়ার্ড: `{FIXED_PASSWORD}`\n\nচেক করে নিচের বাটনে ক্লিক করুন।", reply_markup=admin_markup, parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, "❌ এডমিন গ্রুপে বট এড করা নেই বা আইডি ভুল।")

    elif data.startswith("admin_approve_"):
        parts = data.split("_")
        worker_id = int(parts[2])
        gmail = parts[3]
        
        update_balance(worker_id, 25) 
        
        try:
            bot.send_message(worker_id, f"🟢 **সাকসেস!** আপনার তৈরি করা জিমেইলটি (`{gmail}`) অ্যাডমিন কনফার্ম করেছে। আপনার ব্যালেন্সে ২৫ টাকা যোগ করা হয়েছে।", parse_mode="Markdown")
        except:
            pass
            
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🟢 **স্ট্যাটাস: অ্যাডমিন কনফার্ম করেছে (সাকসেস)**")
        
    elif data.startswith("admin_reject_"):
        parts = data.split("_")
        worker_id = int(parts[2])
        gmail = parts[3]
        
        try:
            bot.send_message(worker_id, f"🔴 **রিজেক্টেড!** আপনার তৈরি করা জিমেইলটি (`{gmail}`) লগইন না হওয়ায় অ্যাডমিন বাতিল করেছে। দয়া করে সঠিক নিয়মে আবার চেষ্টা করুন।", parse_mode="Markdown")
        except:
            pass
            
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🔴 **স্ট্যাটাস: রিজেক্ট করা হয়েছে (লগইন হয়নি)**")
        
    elif data.startswith("paid_"):
        parts = data.split("_")
        worker_id = int(parts[1])
        withdraw_amount = int(parts[2])
        
        update_balance(worker_id, -withdraw_amount)
        
        try:
            bot.send_message(worker_id, f"🎉 আপনার {withdraw_amount} টাকা উইথড্র সফল হয়েছে! অ্যাডমিন আপনার নাম্বারে টাকা পাঠিয়ে দিয়েছে।")
        except:
            pass
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.message.text}\n\n🟢 **স্ট্যাটাস: সফলভাবে পেইড করা হয়েছে**")

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("বট সফলভাবে চালু হয়েছে...")
    bot.polling(none_stop=True)
