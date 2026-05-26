from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

BOT_TOKEN = ""

def keyboard_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("yes", callback_data="yes"), InlineKeyboardButton("no", callback_data="no")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(f"context: {context}\n")
    print(f"context.user_data: {context.user_data}")
    user_data = context.user_data
    user_data['name'] = update.effective_user.first_name
    user_data['language'] = update.effective_user.language_code
    print(user_data.keys())
    print(user_data.values())
    print(user_data.items())    
    await context.bot.send_message(
        chat_id=user_id,
        text="Получен объект типа update",
        reply_markup=keyboard_start()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    keyboard_back = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Назад", callback_data="return_to_start")]
        ]
    )
    if query.data == 'yes':
        await query.edit_message_text(
            text="You sent 'yes'",
            reply_markup=keyboard_back
        )
    elif query.data == 'no':
        await query.edit_message_text(
            text="You sent 'no'. Why??",
            reply_markup=keyboard_back
        )
    elif query.data == "return_to_start":
        await query.edit_message_text(
            text="Получен объект типа update",
            reply_markup=keyboard_start()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
