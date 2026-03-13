import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

BOT_TOKEN = "8693893302:AAFw9dNRMiuD6DyKtkpgg86jOMJ7ZHiGlB8"
API_KEY = "xVTjx7s8rhlQc4WSEiHJp4ugg1MBqKZW0dDwQxvbCyA60bQU"
API_SECRET = "AGJuAHBjRXA21aLMubO7yZlhOzpNXvM98TMeXU7AIuGIiBKspyALheJCu8U6gGkW"

user_credentials = {}
pending_action = {}

def start(update: Update, context):
    update.message.reply_text("👋 أهلاً بك! من فضلك أدخل رقم الموبايل:")

def handle_message(update: Update, context):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    # إدخال بيانات الدخول
    if chat_id not in user_credentials:
        user_credentials[chat_id] = {"phone": text}
        update.message.reply_text("✅ تمام، دلوقتي أدخل كلمة السر:")
    elif "password" not in user_credentials[chat_id]:
        user_credentials[chat_id]["password"] = text
        update.message.reply_text("🎉 تم تسجيل الدخول بنجاح\nاكتب /begin لعرض الخدمات.")
    # إدخال مبلغ العملية
    elif chat_id in pending_action:
        action = pending_action.pop(chat_id)
        phone = user_credentials[chat_id]["phone"]
        password = user_credentials[chat_id]["password"]

        # التحقق أن المدخل رقم صحيح
        if not text.isdigit():
            update.message.reply_text("⚠️ من فضلك أدخل رقم صحيح.")
            pending_action[chat_id] = action
            return

        amount = int(text)

        if action == "recharge":
            payload = {"username": phone, "password": password, "amount": amount}
            response = requests.post(f"{VODAFONE_API_URL}/recharge", json=payload)
            if response.status_code == 200:
                update.message.reply_text(f"✅ تم شحن {amount} جنيه بنجاح")
            else:
                update.message.reply_text("❌ فشل في عملية الشحن")

        elif action == "bill":
            payload = {"username": phone, "password": password, "amount": amount}
            response = requests.post(f"{VODAFONE_API_URL}/pay_bill", json=payload)
            if response.status_code == 200:
                update.message.reply_text(f"✅ تم دفع فاتورة بقيمة {amount} جنيه")
            else:
                update.message.reply_text("❌ فشل دفع الفاتورة")

def show_services(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("💸 شحن رصيد", callback_data='recharge')],
        [InlineKeyboardButton("🧾 دفع فاتورة", callback_data='bill')],
        [InlineKeyboardButton("🌐 باقات الإنترنت", callback_data='internet')],
        [InlineKeyboardButton("⬅️ رجوع", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('📋 اختر الخدمة التي تريدها:', reply_markup=reply_markup)

def button(update: Update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == 'recharge':
        pending_action[chat_id] = "recharge"
        query.edit_message_text(text="💸 من فضلك أدخل مبلغ الشحن:")
    elif query.data == 'bill':
        pending_action[chat_id] = "bill"
        query.edit_message_text(text="🧾 من فضلك أدخل قيمة الفاتورة:")
    elif query.data == 'internet':
        # هنا العميل يختار الباقة من قائمة أزرار
        bundles = [
            [InlineKeyboardButton("📶 باقة 5 جيجا", callback_data='bundle_5')],
            [InlineKeyboardButton("📶 باقة 10 جيجا", callback_data='bundle_10')],
            [InlineKeyboardButton("📶 باقة 20 جيجا", callback_data='bundle_20')]
        ]
        reply_markup = InlineKeyboardMarkup(bundles)
        query.edit_message_text(text="🌐 اختر الباقة:", reply_markup=reply_markup)
    elif query.data.startswith('bundle_'):
        phone = user_credentials[chat_id]["phone"]
        password = user_credentials[chat_id]["password"]
        bundle_id = query.data.replace("bundle_", "")
        payload = {"username": phone, "password": password, "bundle_id": bundle_id}
        response = requests.post(f"{VODAFONE_API_URL}/subscribe_bundle", json=payload)
        if response.status_code == 200:
            query.edit_message_text(text=f"✅ تم الاشتراك في باقة {bundle_id} جيجا")
        else:
            query.edit_message_text(text="❌ فشل الاشتراك في الباقة")
    elif query.data == 'back':
        query.edit_message_text(text="⬅️ رجوع للقائمة السابقة...")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("begin", show_services))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()



