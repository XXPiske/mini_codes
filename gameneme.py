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

BOT_TOKEN = "8685899604:AAHMENpiZTPzqH5umEDF0AYrP1jOWU2qOaE"

(
    ASK_MAIN_MENU, 
    GUESS_SET_LEFT_BOUND, GUESS_SET_RIGHT_BOUND, GUESS_GAME, 
    TWENTYONE_GAME
) = range(5)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Игра выключилась. Нажми /start, чтобы начать играть")
    return ConversationHandler.END

def get_card(card_deck: dict) -> tuple[str, int]:
    card_volume = {
        "A": 11, "K": 4, "Q": 3, "J": 2, "10": 10, "9": 0,
        "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2
    }
    available_cards = [card for card, count in card_deck.items() if count > 0]
    card = random.choice(available_cards)
    card_deck[card] -= 1
    volume = card_volume[card]
    return card, volume

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Угадай число", callback_data="guess_number")],
        [InlineKeyboardButton("21", callback_data="game_21")]
    ])
    text = "Главное меню\n\nВыбери игру"
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
    else:
        await update.effective_message.reply_text(
            text=text,
            reply_markup=keyboard
        )
    return ASK_MAIN_MENU

def keyboard_21(still_playing: bool):
    if still_playing:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Еще", callback_data="21_more", style="success"),
                InlineKeyboardButton("Стоп", callback_data="21_end", style="danger")
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Меню", callback_data="21_back_menu")],
            [InlineKeyboardButton("Сыграть еще раз", callback_data="21_play_again")]
        ])
    return keyboard

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "guess_number":
        await query.edit_message_text("Напиши от какого числа гадаем")
        return GUESS_SET_LEFT_BOUND
    elif query.data == "game_21":
        return await twentyone_start(update, context)

async def twentyone_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    card_deck = {k: 4 for k in ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]}
    card1, volume1 = get_card(card_deck)
    card2, volume2 = get_card(card_deck)
    volume = volume1 + volume2
    message = f"Отлично давай сыграем в 21!\nВы получили {card1} и {card2}"
    if volume > 21:
        await query.edit_message_text(
            text=message + "\nК сожалению, вы сразу же проиграли :(",
            reply_markup=keyboard_21(False)
        )
        context.user_data.clear()
        return TWENTYONE_GAME
    elif volume == 21:
        await query.edit_message_text(
            message + "\nИ сразу же выиграли!!",
            reply_markup=keyboard_21(False)
        )
        context.user_data.clear()
        return TWENTYONE_GAME
    else:
        context.user_data["card_deck"] = card_deck
        context.user_data["volume"] = volume
        await query.edit_message_text(
            text=message + f"\nВсего очков: {volume}",
            reply_markup=keyboard_21(True)
        )
        return TWENTYONE_GAME

async def twentyone_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "21_play_again":
        context.user_data.clear()
        return await twentyone_start(update, context)
    elif query.data == "21_back_menu":
        context.user_data.clear()
        return await start(update, context)

    total_volume = context.user_data["volume"]
    if query.data == "21_more":
        card, volume = get_card(context.user_data["card_deck"])
        total_volume += volume
        message = f"Вытянута карта {card}\nСумма очков: {total_volume}"
        if total_volume > 21:
            await query.edit_message_text(
                text=message + "\nВы проиграли :(",
                reply_markup=keyboard_21(False)
            )
            context.user_data.clear()
            return TWENTYONE_GAME
        elif total_volume == 21:
            await query.edit_message_text(
                text=message + "\nВы выиграли!!",
                reply_markup=keyboard_21(False)
            )
            context.user_data.clear()
            return TWENTYONE_GAME
        else:
            context.user_data["volume"] = total_volume
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard_21(True)
            )
            return TWENTYONE_GAME
    elif query.data == "21_end":
        await query.edit_message_text(
            text=f"Ваша сумма очков: {total_volume}",
            reply_markup=keyboard_21(False)
        )
        context.user_data.clear()
        return TWENTYONE_GAME


# УГАДАЙ ЧИСЛО
async def set_left_bound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    try:
        left_bound = int(user_input)
    except ValueError:
        await update.effective_message.reply_text("Напиши целое число")
        return GUESS_SET_LEFT_BOUND      
    context.user_data["left_bound"] = left_bound
    await update.effective_message.reply_text("Отлично! Теперь напиши до какого числа гадаем")
    return GUESS_SET_RIGHT_BOUND

async def set_right_bound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    try:
        right_bound = int(user_input)
    except ValueError:
        await update.effective_message.reply_text("Напиши целое число")
        return GUESS_SET_RIGHT_BOUND
    
    left_bound = context.user_data.get("left_bound")
    if right_bound <= left_bound:
        await update.effective_message.reply_text("Правая граница должна быть больше левой!")
        return GUESS_SET_RIGHT_BOUND
    context.user_data["right_bound"] = right_bound
    context.user_data["the_chosen_number"] = random.randint(left_bound, right_bound)
    await update.effective_message.reply_text("Отлично, теперь гадай!")
    return GUESS_GAME

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
        return GUESS_GAME
    
    if guess < left_bound or guess > right_bound:
        await update.effective_message.reply_text(f"Число должно быть от {left_bound} до {right_bound}! Попробуй еще раз")
        return GUESS_GAME
    elif guess < the_chosen_number:
        await update.effective_message.reply_text("Больше")
        return GUESS_GAME
    elif guess > the_chosen_number:
        await update.effective_message.reply_text("Меньше")
        return GUESS_GAME
    else:
        await update.effective_message.reply_text(f"Ты победил! Было загадано число {the_chosen_number}!")
        context.user_data.clear()
        return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    main_conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            ASK_MAIN_MENU: [CallbackQueryHandler(main_menu_handler, pattern="^(guess_number|game_21)$")],

            GUESS_SET_LEFT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_left_bound)],
            GUESS_SET_RIGHT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_right_bound)],
            GUESS_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_a_guess)],

            TWENTYONE_GAME: [CallbackQueryHandler(twentyone_game, pattern="^21_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(main_conv)
    app.run_polling()

if __name__ == '__main__':
    main()
