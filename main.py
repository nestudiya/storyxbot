```python
import os
import requests
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from dotenv import load_dotenv

load_dotenv()

# Настройки
BOT_TOKEN = '7668252504:AAFSuBG8vUKVH8REezRUBJNBwQTT7oPZMZo'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Состояния диалога
CHOOSING, GAME_START, CHOOSING_OPTION, END = range(4)

# Список жанров
GENRES = ["Фэнтези", "Фантастика", "Детектив", "Роман", "Приключения"]

# Создание функции генерации сюжета и персонажей с помощью OpenAI
def generate_story(genre):
    response = openai_client.completions.create(
        model="text-davinci-003",
        prompt=f"Напиши краткий сюжет рассказа в жанре {genre}.",
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Создание функции генерации вариантов для голосования с помощью OpenAI
def generate_options(story_text):
    response = openai_client.completions.create(
        model="text-davinci-003",
        prompt=f"Напиши вариант продолжения сюжета:\n\n{story_text}",
        max_tokens=50,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Обработка команды /start
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name}! \n\n"
        f"Я - бот, который может генерировать интересные истории! \n\n"
        f"Хочешь сыграть со мной? \n\n"
        f"Выбери жанр истории: {', '.join(GENRES)}."
    )
    return CHOOSING

# Обработка выбора жанра
def genre_chosen(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if update.message.text in GENRES:
        context.user_data['genre'] = update.message.text
        story_text = generate_story(context.user_data['genre'])
        options = generate_options(story_text)
        update.message.reply_text(f"Отлично! \n\n{story_text}\n\nЧто будет дальше? \n\n{options}")
        return CHOOSING_OPTION
    else:
        update.message.reply_text("Извини, я не понял. \n\nВыбери жанр истории: {', '.join(GENRES)}.")
        return CHOOSING

# Обработка выбора варианта
def option_chosen(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user = update.effective_user
    data = query.data
    
    # Проверка наличия данных
    if not data or len(data) == 0:
        query.answer("Произошла ошибка при выборе варианта. Попробуйте снова.")
        return CHOOSING_OPTION
    
    context.user_data["selected_option"] = data
    story_text = generate_story(context.user_data["genre"])
    update.message.reply_text(f"{story_text}\n\nЧто будет дальше?")
    return CHOOSING_OPTION
