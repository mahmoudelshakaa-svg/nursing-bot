import telebot
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# تخزين الشهور المفتوحة لكل طالب
# الشكل: {user_id: {"2026-10", "2026-11", ...}}
subscriptions = {}

def get_current_month():
    now = datetime.now()
    return now.strftime("%Y-%m")  # مثال: 2026-10

def has_month(user_id, month):
    return user_id in subscriptions and month in subscriptions[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    current = get_current_month()

    if has_month(user_id, current):
        bot.reply_to(message, f"✅ اشتراكك شغال لشهر {current}\n\nابعت اسم المحاضرة اللي عايزها.")
    else:
        text = f"""
مرحباً بك في بوت شروحات التمريض 🩺

الاشتراك الحالي: شهر {current}

للاشتراك:
1. ادفع على فودافون كاش
2. ابعت صورة الإيصال هنا

بعد التأكيد هيتفتح لك محتوى الشهر.
المحتوى اللي بيفتح لك بيفضل معاك للأبد.
"""
        bot.reply_to(message, text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    current = get_current_month()

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(
        ADMIN_ID,
        f"طلب اشتراك جديد\n"
        f"الاسم: {name}\n"
        f"الآي دي: `{user_id}`\n"
        f"الشهر الحالي: {current}\n\n"
        f"عشان تفعّل اكتب:\n"
        f"`/approve {user_id} {current}`",
        parse_mode="Markdown"
    )
    bot.reply_to(message, "تم استلام صورة الدفع ✅\nانتظر التأكيد من الإدارة.")

@bot.message_handler(commands=['approve'])
def approve(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        month = parts[2] if len(parts) > 2 else get_current_month()

        if user_id not in subscriptions:
            subscriptions[user_id] = set()
        subscriptions[user_id].add(month)

        bot.send_message(user_id, f"✅ تم تفعيل محتوى شهر {month} ليك.\nالمحتوى ده هيفضل معاك.")
        bot.reply_to(message, f"تم تفعيل شهر {month} للطالب {user_id}")
    except:
        bot.reply_to(message, "استخدم الأمر كده:\n/approve 123456789 2026-10")

@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        month = parts[2] if len(parts) > 2 else get_current_month()

        if user_id not in subscriptions:
            subscriptions[user_id] = set()
        subscriptions[user_id].add(month)

        bot.send_message(user_id, f"✅ تم إضافة محتوى شهر {month} ليك.")
        bot.reply_to(message, f"تم إضافة شهر {month} للطالب {user_id}")
    except:
        bot.reply_to(message, "استخدم الأمر كده:\n/add 123456789 2026-10")

@bot.message_handler(commands=['mystatus'])
def my_status(message):
    user_id = message.from_user.id
    if user_id not in subscriptions or not subscriptions[user_id]:
        bot.reply_to(message, "ما عندكش أي شهور مفتوحة حالياً.")
    else:
        months = "\n".join(sorted(subscriptions[user_id]))
        bot.reply_to(message, f"الشهور المفتوحة عندك:\n{months}")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    current = get_current_month()

    if not has_month(user_id, current):
        bot.reply_to(message, f"❌ محتوى شهر {current} مش مفتوح عندك.\nابعت صورة إيصال الدفع أولاً.")
        return

    bot.reply_to(message, "المحاضرات هتتضاف قريب.\nابعت اسم المحاضرة.")

print("Bot is running...")
bot.infinity_polling()
