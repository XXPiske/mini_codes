from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import random

BOT_TOKEN = ""

SET_LEFT_BOUND, SET_RIGHT_BOUND, GUESSING = range(3)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Игра выключилась. Нажми /start, чтобы начать играть")
    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Давай сыграем в угадай число! Напиши от какого числа гадаем")
    context.user_data.clear() # очищаем словарь перед стартом
    return SET_LEFT_BOUND

async def set_left_bound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    try:
        left_bound = int(user_input)
        context.user_data["left_bound"] = left_bound
        await update.effective_message.reply_text("Отлично! Теперь напиши до какого числа гадаем")
        return SET_RIGHT_BOUND
    except ValueError:
        await update.effective_message.reply_text("Напиши целое число")
        return SET_LEFT_BOUND

async def set_right_bound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    try:
        right_bound = int(user_input)
    except ValueError:
        await update.effective_message.reply_text("Напиши целое число")
        return SET_RIGHT_BOUND
    
    left_bound = context.user_data.get("left_bound")
    if right_bound <= left_bound:
        await update.effective_message.reply_text("Правая граница должна быть больше левой!")
        return SET_RIGHT_BOUND
    context.user_data["right_bound"] = right_bound
    context.user_data["the_chosen_number"] = random.randint(left_bound, right_bound)
    await update.effective_message.reply_text("Отлично, теперь гадай!")
    return GUESSING


async def check_a_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    left_bound = context.user_data.get("left_bound")
    right_bound = context.user_data.get("right_bound")
    the_chosen_number = context.user_data.get("the_chosen_number")
    if None in (left_bound, right_bound, the_chosen_number):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Что-то пошло не так. Начни игру заново /start"
        )
        return ConversationHandler.END
    
    try:
        guess = int(user_input)
    except ValueError:
        await update.effective_message.reply_text(f"Напиши целое число от {left_bound} до {right_bound}")
        return GUESSING
    
    if guess < left_bound or guess > right_bound:
        await update.effective_message.reply_text(f"Число должно быть от {left_bound} до {right_bound}! Попробуй еще раз")
        return GUESSING
    elif guess < the_chosen_number:
        await update.effective_message.reply_text("Больше")
        return GUESSING
    elif guess > the_chosen_number:
        await update.effective_message.reply_text("Меньше")
        return GUESSING
    else:
        await update.effective_message.reply_text(f"Ты победил! Было загадано число {the_chosen_number}!")
        return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    main_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SET_LEFT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_left_bound)],
            SET_RIGHT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_right_bound)],
            GUESSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_a_guess)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(main_conv)
    app.run_polling()

if __name__ == '__main__':
    main()