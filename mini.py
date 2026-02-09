
## 3. Упрощенная версия для тестирования `bot_simple.py`


import telebot
from telebot import types
import logging
import json
from datetime import datetime

# Настройка
TOKEN = "8514338899:AAEQV5ERm5WaK-7rhtFIQpgt-A165B7rzJI"
CHANNEL_ID = "@daypinchik"  # Создайте тестовый канал

bot = telebot.TeleBot(TOKEN)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_action(user, action):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 👤 @{user.username or user.id} → {action}")

# Команды
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    log_action(user, "команда /start")
    
    # Устанавливаем аватар (нужен файл avatar.jpg)
    try:
        with open('avatar.jpg', 'rb') as photo:
            bot.set_chat_photo(message.chat.id, photo)
    except:
        pass
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Купить звезды", "📤 Опубликовать", "📊 Статистика")
    
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {user.first_name}!\n\n"
        f"💰 *Цены:*\n"
        f"• Фото: 250 Telegram Stars\n"
        f"• Видео: 1500 Telegram Stars\n\n"
        f"⚡ Для покупки звезд нажмите кнопку ниже:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "💰 Купить звезды")
def buy_stars(message):
    user = message.from_user
    log_action(user, "запросил покупку звезд")
    
    markup = types.InlineKeyboardMarkup()
    
    # Тестовые платежи (в реальности нужно настроить Stripe)
    markup.add(
        types.InlineKeyboardButton("💳 Настроить платежи", url="https://core.telegram.org/bots/payments")
    )
    
    bot.send_message(
        message.chat.id,
        "💳 *Покупка Telegram Stars*\n\n"
        "Для приема платежей необходимо:\n"
        "1. Зарегистрироваться на Stripe.com\n"
        "2. Получить API ключи\n"
        "3. Настроить в @BotFather\n\n"
        "📚 Документация: https://core.telegram.org/bots/payments",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = message.from_user
    log_action(user, "отправил фото")
    
    bot.send_message(
        message.chat.id,
        f"📸 Фото получено!\n\n"
        f"*Для публикации нужно:*\n"
        f"1. Настроить платежи (/buy)\n"
        f"2. Пополнить баланс\n"
        f"3. Оплатить 250 Telegram Stars",
        parse_mode='Markdown'
    )

# Запуск
print("🤖 Бот запущен...")
print("🕒 Логи действий:")
print("=" * 50)
bot.polling(none_stop=True)