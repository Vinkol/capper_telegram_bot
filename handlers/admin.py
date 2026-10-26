# handlers/admin.py
import os
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMIN_ID, CHANNEL_ID, BK_LINK
import database as db
from handlers.image_generator import generate_stats_image
from handlers.bet_image_generator import generate_bet_image  # Импортируем новый генератор карточек

def register_handlers(bot: TeleBot):
    
    # Вывод отчета-картинки по команде /stats в ЛС админа
    @bot.message_handler(commands=['stats'], func=lambda message: message.from_user.id == ADMIN_ID and message.chat.type == "private")
    def send_stats_report(message: Message):
        bot.send_message(message.chat.id, "📊 Генерирую актуальный отчет статистики, подождите...")
        generate_stats_image()
        with open("stats_report.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption="📈 Ваша актуальная статистика на текущий момент.")

    # Инструкция по команде /help
    @bot.message_handler(commands=['help'], func=lambda message: message.from_user.id == ADMIN_ID and message.chat.type == "private")
    def send_help_info(message: Message):
        help_text = (
            "❓ **Как публиковать прогнозы:**\n\n"
            "Отправьте мне сообщение в формате через запятую:\n"
            "`Команда1 - Команда2, Ставка, Коэффициент`\n\n"
            "Пример:\n"
            "`Реал - Барселона, ТБ 2.5, 1.85`"
        )
        bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

    # Обработка сообщений с прогнозами от админа в ЛС
    @bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.chat.type == "private")
    def handle_prediction(message: Message):
        text = message.text
        
        # Парсим текст по запятым
        try:
            parts = [p.strip() for p in text.split(",")]
            if len(parts) < 3:
                raise ValueError
            
            match_name = parts[0]
            bet_type = parts[1]
            odds = float(parts[2])
        except ValueError:
            bot.send_message(message.chat.id, "❌ Ошибка формата! Пишите так:\n*Реал - Барселона, ТБ 2.5, 1.85*", parse_mode="Markdown")
            return

        # 1. Сохраняем ставку в базу данных
        bet_id = db.add_bet(match_name, bet_type, odds)

        # 2. Генерируем красивую картинку прогноза
        generate_bet_image(match_name, bet_type, odds)

        # Текст для описания под картинкой в канале
        caption_text = f"🔥 Новый прогноз в базе под №{bet_id}! Проверить коэффициенты и сделать ставку можно на сайте букмекера 👇"

        # Кнопка под постом в канале
        channel_keyboard = InlineKeyboardMarkup()
        channel_keyboard.add(InlineKeyboardButton(text="📱 Сделать ставку в БК", url=BK_LINK))

        # 3. Отправляем картинку в канал (если CHANNEL_ID настроен)
        if CHANNEL_ID != 0:
            try:
                with open("bet_card.png", "rb") as photo:
                    bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption_text, reply_markup=channel_keyboard)
                status_msg = f"🚀 Прогноз №{bet_id} успешно опубликован в группе в виде карточки!\n"
            except Exception as e:
                status_msg = f"⚠️ Прогноз сохранен в БД, но не опубликован в группе (Ошибка: {e})\n"
        else:
            status_msg = f"📦 Прогноз №{bet_id} сохранен в БД и сгенерирован (ID группы не настроен).\n"
        
        # 4. Админу в ЛС присылаем пульт управления результатом
        admin_keyboard = InlineKeyboardMarkup()
        admin_keyboard.row(
            InlineKeyboardButton(text="✅ Выигрыш", callback_data=f"result_win_{bet_id}"),
            InlineKeyboardButton(text="❌ Проигрыш", callback_data=f"result_lose_{bet_id}")
        )
        admin_keyboard.add(InlineKeyboardButton(text="🔄 Возврат", callback_data=f"result_return_{bet_id}"))
        
        bot.send_message(message.chat.id, f"{status_msg}Укажите результат, когда матч завершится:", reply_markup=admin_keyboard)

    # Обработка нажатия на кнопки результатов в ЛС админа
    @bot.callback_query_handler(func=lambda call: call.data.startswith("result_"))
    def process_bet_result(call: CallbackQuery):
        data_parts = call.data.split("_")
        status = data_parts[1]  # win, lose, return
        bet_id = int(data_parts[2])

        db.update_bet_status(bet_id, status)

        status_markers = {"win": "✅ Выигрыш", "lose": "❌ Проигрыш", "return": "🔄 Возврат"}
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📊 Ставка №{bet_id} обновлена: *{status_markers[status]}*",
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, text="Статус сохранен!")
