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
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

(
    ASK_MAIN_MENU, 
    GUESS_SET_LEFT_BOUND, GUESS_SET_RIGHT_BOUND, GUESS_GAME, 
    TWENTYONE_GAME,
    HANGMAN_START, HANGMAN_GAME
) = range(7)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Игра выключилась. Нажми /start, чтобы начать играть")
    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Угадай число", callback_data="guess_number")],
        [InlineKeyboardButton("21", callback_data="game_21")],
        [InlineKeyboardButton("Виселица", callback_data="hangman")]
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

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "guess_number":
        await query.edit_message_text("Напиши от какого числа гадаем")
        return GUESS_SET_LEFT_BOUND
    elif query.data == "game_21":
        return await twentyone_start(update, context)
    elif query.data == "hangman":
        return await hangman_set_dificulty(update, context)

# ======================================================================
# ДВАДЦАТЬ ОДНО (ОЧКО)
# ======================================================================
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
            [InlineKeyboardButton("Сыграть еще раз", callback_data="21_play_again", style="primary")],
            [InlineKeyboardButton("Меню", callback_data="21_back_menu")]
        ])
    return keyboard

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
# ======================================================================



# ======================================================================
# УГАДАЙ ЧИСЛО
# ======================================================================
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
# ======================================================================



# ======================================================================
# ВИСЕЛИЦА
# _______
# |/      |
# |       о
# |      /|\
# |      /|
# |________
# ======================================================================
RU_ALPHABET = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]

def get_word(min_len: int, max_len: int) -> str:
    with open("words.txt", "r", encoding="utf-8") as f:
        words = f.read().splitlines()
    words = [word for word in words if min_len < len(word) < max_len]
    word = random.choice(words)
    return word

def is_letter(text: str) -> bool:
    if len(text) > 1:
        return False
    elif text not in RU_ALPHABET:
        return False
    return True

def get_picture_by_mistake(mistake: int) -> str:
    if mistake <= 0:
        return ""
    elif mistake == 1:
        return "\n|\n|\n|\n|\n|________" # пол и столб
    elif mistake == 2:
        return "_______\n|/\n|\n|\n|\n|________" # перекладина
    elif mistake == 3:
        return "_______\n|/\n|\n|       |\n|\n|________" # тело
    elif mistake == 4:
        return "_______\n|/       \n|        \n|       | \n|     / \n|________" # нога
    elif mistake == 5:
        return "_______\n|/       \n|        \n|       |\\\n|     /|\n|________" # рука и вторая нога
    elif mistake == 6:
        return "_______\n|/       \n|        \n|      /|\\\n|      /|\n|________" # вторая рука
    elif mistake >= 7:
        return "_______\n|/      |\n|       о\n|      /|\\\n|      /|\n|________" # голова и веревка (проигрыш)

async def hangman_set_dificulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Легкий", callback_data="hangman_easy")],
        [InlineKeyboardButton("Средний", callback_data="hangman_medium")],
        [InlineKeyboardButton("Сложный", callback_data="hangman_hard")]
    ])
    await query.edit_message_text(
        "Выбери сложность\n\nЛегкий: слова до 5 букв\nСредний: слова от 6 до 9 букв\nСложный: слова более 10 букв",
        reply_markup=keyboard
    )
    return HANGMAN_START

async def hangman_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "hangman_easy":
        word = get_word(0, 6)
    elif query.data == "hangman_medium":
        word = get_word(5, 10)
    elif query.data == "hangman_hard":
        word = get_word(9, 20) # пока максимум оставим 20 букв

    hidden_letters = list(word)
    for i, letter in enumerate(hidden_letters):
        hidden_letters[i] = "_" # заменяем все буквы на _
    context.user_data["alphabet"] = RU_ALPHABET.copy()
    context.user_data["word"] = word
    context.user_data["hidden_letters"] = hidden_letters
    context.user_data["mistake"] = 0
    await query.edit_message_text(f"Напиши любую букву\n{" ".join(hidden_letters)}\n\n{" ".join(RU_ALPHABET)}")
    return HANGMAN_GAME

async def hangman_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    letter = user_input.lower()
    check_letter = is_letter(letter)
    if check_letter is False:
        await update.effective_message.reply_text("Напиши только 1 букву")
        return HANGMAN_GAME

    alphabet = context.user_data["alphabet"]
    if letter not in alphabet:
        await update.effective_message.reply_text("Ты уже использовал эту букву")
        return HANGMAN_GAME

    alphabet[alphabet.index(letter)] = "_" # убираем букву из алфавита
    word = context.user_data["word"]
    hidden_letters = context.user_data["hidden_letters"]
    mistake = context.user_data["mistake"]
    picture = get_picture_by_mistake(mistake)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сыграть еще раз", callback_data="hangman_restart", style="primary")],
        [InlineKeyboardButton("Меню", callback_data="hangman_back_menu")]
    ])
    if letter in list(word): # угадал 
        for i, l in enumerate(word):
            if l == letter:
                hidden_letters[i] = letter

        if "_" not in hidden_letters: # все разгадал (выигрыш)
            await update.effective_message.reply_text(
                text=f"Ты выиграл!\n{word}\n{picture}",
                reply_markup=keyboard
            )
            context.user_data.clear()
            return HANGMAN_GAME
        else: # угадал (играем дальше)
            await update.effective_message.reply_text(f"Угадал!\n{" ".join(hidden_letters)}\n\n{" ".join(alphabet)}\n{picture}")
            return HANGMAN_GAME
    else: # не угадал (играем дальше)
        mistake += 1
        picture = get_picture_by_mistake(mistake)
        if mistake == 7: # проигрыш
            await update.effective_message.reply_text(
                text=f"Ты проиграл!\nЗагаданное слово: {word}\n{picture}",
                reply_markup=keyboard
            )
            context.user_data.clear()
            return HANGMAN_GAME
        else:
            context.user_data["mistake"] = mistake
            context.user_data["alphabet"] = alphabet
            context.user_data["hidden_letters"] = hidden_letters
            await update.effective_message.reply_text(f"Не угадал!\n{" ".join(hidden_letters)}\n\n{" ".join(alphabet)}\n{picture}")
            return HANGMAN_GAME

async def hangman_end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    if query.data == "hangman_restart":
        return await hangman_set_dificulty(update, context)
    elif query.data == "hangman_back_menu":
        return await start(update, context)
# ======================================================================



def main():
    app = Application.builder().token(BOT_TOKEN).build()
    main_conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            ASK_MAIN_MENU: [CallbackQueryHandler(main_menu_handler, pattern="^(guess_number|game_21|hangman)$")],

            GUESS_SET_LEFT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_left_bound)],
            GUESS_SET_RIGHT_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_right_bound)],
            GUESS_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_a_guess)],

            TWENTYONE_GAME: [CallbackQueryHandler(twentyone_game, pattern="^21_")],
            
            HANGMAN_START: [CallbackQueryHandler(hangman_start, pattern="^hangman_")],
            HANGMAN_GAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, hangman_game),
                CallbackQueryHandler(hangman_end_game, pattern="^hangman_(restart|back_menu)$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(main_conv)
    app.run_polling()

if __name__ == '__main__':
    main()
