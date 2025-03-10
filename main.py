import os
import subprocess
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# إعداد اللوج الخاص بالبوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# التوكن الخاص بالبورت
TOKEN = '7431043644:AAHBlKvRfy_BoK34Puu81F85d7itqPfN-_4'

# وظيفة لتحميل المكتبات إذا كانت مفقودة
def install_requirements():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot"])
    except subprocess.CalledProcessError:
        logger.error("حدث خطأ أثناء تثبيت المكتبات المطلوبة.")

# وظيفة لتشغيل السكربت
def run_code(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, text="الكود يعمل")

    # إضافة زر للإيقاف
    keyboard = [
        [InlineKeyboardButton("إيقاف تشغيل الكود", callback_data='stop')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = context.bot.send_message(chat_id, text="Printing...\n--------------\n", reply_markup=reply_markup)

    # تشغيل الكود المرسل
    code_file = update.message.document
    file_path = f"/tmp/{code_file.file_name}"

    # تنزيل الملف
    code_file.get_file().download(file_path)

    # فحص وتثبيت المكتبات اللازمة
    install_requirements()

    # تشغيل السكربت وحفظ مخرجاته
    try:
        process = subprocess.Popen(['python3', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # قراءة المخرجات من الكود بشكل تدريجي
        stdout = ''
        while True:
            output = process.stdout.read(1024).decode()  # قراءة جزء من المخرجات
            if output == '' and process.poll() is not None:
                break
            if output:
                stdout += output
                context.bot.edit_message_text(
                    text=f"Printing...\n--------------\n{stdout}", 
                    chat_id=chat_id, 
                    message_id=message.message_id
                )

        stderr = process.stderr.read().decode()
        if stderr:
            context.bot.send_message(chat_id, text=f"خطأ في تنفيذ الكود:\n{stderr}")

    except Exception as e:
        context.bot.send_message(chat_id, text=f"حدث خطأ أثناء تشغيل الكود: {str(e)}")

# وظيفة لإيقاف الكود
def stop_code(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat_id
    context.bot.send_message(chat_id, text="تم إيقاف تشغيل الكود.")
    # هنا يمكنك إضافة منطق لإيقاف العمليات الجارية إذا كانت ضرورية
    update.callback_query.answer()

# وظيفة للبدء
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أرسل لي ملف بايثون وسأقوم بتشغيله.")

# وظيفة للرد على الرسائل
def handle_messages(update: Update, context: CallbackContext):
    update.message.reply_text("أرسل لي ملف بايثون.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/python"), run_code))
    dp.add_handler(CallbackQueryHandler(stop_code, pattern='stop'))
    dp.add_handler(MessageHandler(Filters.text, handle_messages))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
