import telebot, sqlite3, random, string, time, requests
from telebot import types
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
API_TOKEN = '8835073880:AAFmtwmH1BN9quuFAW8XA2dDjNT_G7TeSVY' # আপনার টোকেন এখানে আছে
bot = telebot.TeleBot(API_TOKEN)
GMAIL_GROUP_ID = -1003929483102       
WITHDRAW_GROUP_ID = -1003951801755 
TASK_CHANNEL_LINK = "https://t.me/uxgmail"
FIXED_PASSWORD = "Blacknoob8"

task_rate = 15 

# --- ডাটাবেজ ও ফাংশন ---
def get_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, tasks_done INTEGER DEFAULT 0)''')
    return conn

# ওটিপি পাওয়ার জন্য API ফাংশন
def get_email():
    url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
    return requests.get(url).json()[0]

def check_inbox(login, domain):
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    messages = requests.get(url).json()
    if messages:
        msg_id = messages[0]['id']
        msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
        return requests.get(msg_url).json()['textBody']
    return None

# --- হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Execute Task", "📧 Get Temp Mail", "📊 Intelligence Report", "💸 Withdraw")
    bot.send_message(m.chat.id, "🤖 *SYNTHETIC NEXUS V5.0*\nমেনু থেকে আপনার প্রয়োজন সিলেক্ট করুন:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📧 Get Temp Mail")
def handle_get_mail(m):
    email = get_email()
    bot.send_message(m.chat.id, f"✅ আপনার অস্থায়ী মেইল:\n`{email}`\n\n_আমি ৬০ সেকেন্ড অপেক্ষা করছি আপনার মেইলের জন্য..._", parse_mode="Markdown")
    login, domain = email.split('@')
    for _ in range(12):
        time.sleep(5)
        content = check_inbox(login, domain)
        if content:
            bot.send_message(m.chat.id, f"📩 নতুন মেইল এসেছে:\n\n{content}")
            break
    else:
        bot.send_message(m.chat.id, "❌ সময় শেষ! কোনো মেইল পাওয়া যায়নি।")

# --- আগের সব ফাংশন (উইথড্র ও টাস্ক লজিক আগের কোডের মতোই থাকবে) ---
@bot.message_handler(func=lambda m: True)
def menu(m):
    if m.text == "🎁 Execute Task":
        # আপনার আগের টাস্ক জেনারেটর লজিক এখানে থাকবে
        pass
    # অন্যান্য বাটন লজিক এখানে যোগ করুন

if __name__ == '__main__':
    Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
