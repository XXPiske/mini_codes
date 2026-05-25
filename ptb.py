from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

BOT_TOKEN = ''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update:
        print(f"class update: {update}\n")
        print(f"class update.message: {update.message}\n")
        print(f"class update.message.from_user: {update.message.from_user}\n")
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Получен объект типа update"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()