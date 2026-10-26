# main.py
from telebot import TeleBot
from telebot.types import BotCommand
from config import BOT_TOKEN
from handlers import admin
import database as db

def set_bot_commands(bot: TeleBot):
    # Создаем список команд, которые будут видны в меню
    commands = [
        BotCommand("stats", "📊 Посмотреть текущую статистику"),
        BotCommand("help", "❓ Инструкция по формату прогнозов")
    ]
    bot.set_my_commands(commands)

def main():
    # Инициализируем базу данных при старте
    db.init_db()

    # Создаем объект бота
    bot = TeleBot(token=BOT_TOKEN)

    # Устанавливаем меню команд
    set_bot_commands(bot)

    # Регистрируем наши обработчики событий
    admin.register_handlers(bot)

    print("Бот успешно запущен и готов к работе!")
    
    # Запускаем бесконечный опрос серверов Telegram
    bot.infinity_polling()

if __name__ == "__main__":
    main()
