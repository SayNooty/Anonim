import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
import telebot
from telebot import types
from telebot.types import LabeledPrice
import requests
from io import BytesIO

# ========== КОНФИГУРАЦИЯ ==========
TOKEN = "8514338899:AAEQV5ERm5WaK-7rhtFIQpgt-A165B7rzJI"
CHANNEL_ID = "@daypinchik"  # Создайте тестовый канал!

# Цены в Telegram Stars
PRICE_PHOTO = 250
PRICE_VIDEO = 1500

# Система хранения данных
USER_DATA_FILE = "users_data.json"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== АВАТАР БОТА ==========
def set_bot_avatar():
    """Устанавливаем аватар для бота"""
    try:
        # Создаем простой аватар программно или используем готовый файл
        avatar_urls = [
            "https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/Resources/art/icon128.png",
            "https://cdn-icons-png.flaticon.com/512/5968/5968966.png",
            "https://cdn-icons-png.flaticon.com/512/3536/3536666.png"
        ]
        
        # Пытаемся скачать и установить аватар
        response = requests.get(avatar_urls[1])
        if response.status_code == 200:
            # Сохраняем временный файл
            with open("temp_avatar.png", "wb") as f:
                f.write(response.content)
            
            # Устанавливаем аватар (требуются права администратора)
            bot.set_my_profile_photo(open("temp_avatar.png", "rb"))
            print("✅ Аватар бота установлен")
            
            # Удаляем временный файл
            os.remove("temp_avatar.png")
            
    except Exception as e:
        print(f"⚠️ Не удалось установить аватар: {e}")
        print("ℹ️ Аватар можно установить через @BotFather")

# ========== СТРУКТУРА ДАННЫХ ==========
class UserData:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.verified = False
        self.username = None
        self.first_name = None
        self.stars_balance = 1000  # Стартовый баланс для тестирования
        self.pending_content = None
        self.last_active = datetime.now().isoformat()
        self.total_spent = 0
        self.avatar_url = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'verified': self.verified,
            'username': self.username,
            'first_name': self.first_name,
            'stars_balance': self.stars_balance,
            'pending_content': self.pending_content,
            'last_active': self.last_active,
            'total_spent': self.total_spent,
            'avatar_url': self.avatar_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        user = cls(data['user_id'])
        user.verified = data.get('verified', False)
        user.username = data.get('username')
        user.first_name = data.get('first_name')
        user.stars_balance = data.get('stars_balance', 1000)
        user.pending_content = data.get('pending_content')
        user.last_active = data.get('last_active', datetime.now().isoformat())
        user.total_spent = data.get('total_spent', 0)
        user.avatar_url = data.get('avatar_url')
        return user

class DataStorage:
    def __init__(self, filename: str):
        self.filename = filename
        self.users: Dict[int, UserData] = {}
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = {int(k): UserData.from_dict(v) for k, v in data.items()}
                self.log(f"Загружены данные {len(self.users)} пользователей")
        except Exception as e:
            self.log_error(f"Ошибка загрузки: {e}")
            self.users = {}
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            data = {str(k): v.to_dict() for k, v in self.users.items()}
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_error(f"Ошибка сохранения: {e}")
    
    def get_user(self, user_id: int, username: str = None, first_name: str = None) -> UserData:
        """Получение данных пользователя"""
        if user_id not in self.users:
            self.users[user_id] = UserData(user_id)
            self.users[user_id].username = username
            self.users[user_id].first_name = first_name
            self.save_data()
            self.log(f"Создан новый пользователь: {first_name} (@{username}) ID: {user_id}")
        else:
            if username and self.users[user_id].username != username:
                self.users[user_id].username = username
            if first_name and self.users[user_id].first_name != first_name:
                self.users[user_id].first_name = first_name
            self.save_data()
        
        return self.users[user_id]
    
    def update_user(self, user: UserData):
        """Обновление данных пользователя"""
        user.last_active = datetime.now().isoformat()
        self.users[user.user_id] = user
        self.save_data()
    
    def log(self, message: str):
        """Логирование в консоль"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def log_error(self, message: str):
        """Логирование ошибок"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ ОШИБКА: {message}")

# Инициализация
storage = DataStorage(USER_DATA_FILE)
bot = telebot.TeleBot(TOKEN)

# ========== КОМАНДЫ БОТА ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    """Команда /start"""
    user = message.from_user
    user_data = storage.get_user(user.id, user.username, user.first_name)
    
    storage.log(f"👤 @{user.username or user.id} ({user.first_name}) → команда /start")
    
    welcome_text = f"""
🎬 *Content Publisher Bot*
👋 Добро пожаловать, {user.first_name}!

💰 *Система Telegram Stars:*
• 📸 Фотография: {PRICE_PHOTO} ⭐
• 🎥 Видео: {PRICE_VIDEO} ⭐

📋 *Как начать:*
1. Пройдите верификацию (отправьте фото/видео)
2. Пополните баланс (команда /buy)
3. Выберите тип контента
4. Оплатите и опубликуйте

⚡ *Ваш баланс:* {user_data.stars_balance} Telegram Stars
"""
    
    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("✅ Пройти верификацию"),
        types.KeyboardButton("💰 Мой баланс"),
        types.KeyboardButton("📤 Опубликовать"),
        types.KeyboardButton("🛒 Купить звезды")
    )
    
    # Пытаемся установить аватар пользователя в профиль бота
    try:
        # Для теста - установим эмодзи как фото профиля
        bot.set_my_profile_photo(open("bot_avatar.png", "rb"))
    except:
        pass
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "✅ Пройти верификацию")
def verification_button(message):
    """Кнопка верификации"""
    user = message.from_user
    storage.log(f"👤 @{user.username or user.id} → начал верификацию")
    
    verification_text = """
🔐 *ВЕРИФИКАЦИЯ АККАУНТА*

Для использования бота необходимо пройти верификацию.

📤 *Отправьте для верификации:*
• Любое фото
• Или короткое видео
• Или видеосообщение (кружок)

⚡ *После верификации вы получите:*
• Доступ к публикации контента
• Стартовые 1000 Telegram Stars
• Возможность покупать звезды

Просто отправьте фото или видео в этот чат!
"""
    
    bot.send_message(message.chat.id, verification_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "💰 Мой баланс")
def balance_button(message):
    """Кнопка баланса"""
    user = message.from_user
    user_data = storage.get_user(user.id, user.username, user.first_name)
    
    balance_text = f"""
💰 *ВАШ БАЛАНС*

Telegram Stars: *{user_data.stars_balance} ⭐*
Всего потрачено: *{user_data.total_spent} ⭐*

📊 *Стоимость публикаций:*
• 📸 Фотография: {PRICE_PHOTO} ⭐
• 🎥 Видео: {PRICE_VIDEO} ⭐

💎 *Доступно публикаций:*
• Фото: *{user_data.stars_balance // PRICE_PHOTO} шт.*
• Видео: *{user_data.stars_balance // PRICE_VIDEO} шт.*
"""
    
    bot.send_message(message.chat.id, balance_text, parse_mode='Markdown')
    storage.log(f"👤 @{user.username or user.id} → проверил баланс")

@bot.message_handler(func=lambda message: message.text == "🛒 Купить звезды")
def buy_stars_button(message):
    """Кнопка покупки звезд"""
    user = message.from_user
    storage.log(f"👤 @{user.username or user.id} → запросил покупку звезд")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    packages = [
        (100, "$1.00", "buy_100"),
        (500, "$5.00", "buy_500"), 
        (1000, "$10.00", "buy_1000"),
        (2500, "$25.00", "buy_2500"),
        (5000, "$50.00", "buy_5000"),
        (10000, "$100.00", "buy_10000")
    ]
    
    for stars, price, callback in packages:
        markup.add(types.InlineKeyboardButton(
            f"{stars} ⭐ - {price}",
            callback_data=callback
        ))
    
    markup.add(types.InlineKeyboardButton(
        "⚙️ Настроить платежи",
        url="https://core.telegram.org/bots/payments"
    ))
    
    bot.send_message(
        message.chat.id,
        "💳 *ПОКУПКА TELEGRAM STARS*\n\n"
        "Выберите пакет для покупки:\n"
        "1 Telegram Star = $0.01\n\n"
        "💰 *Для тестирования:*\n"
        "Используйте команду /addstars [количество]\n"
        "(только для администраторов)",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "📤 Опубликовать")
def publish_button(message):
    """Кнопка публикации"""
    user = message.from_user
    user_data = storage.get_user(user.id, user.username, user.first_name)
    
    if not user_data.verified:
        bot.send_message(
            message.chat.id,
            "❌ *Сначала пройдите верификацию!*\n\n"
            "Нажмите кнопку '✅ Пройти верификацию'",
            parse_mode='Markdown'
        )
        return
    
    storage.log(f"👤 @{user.username or user.id} → начал публикацию")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"📸 Фото ({PRICE_PHOTO} ⭐)", callback_data='publish_photo'),
        types.InlineKeyboardButton(f"🎥 Видео ({PRICE_VIDEO} ⭐)", callback_data='publish_video')
    )
    
    bot.send_message(
        message.chat.id,
        f"📤 *ВЫБЕРИТЕ ТИП КОНТЕНТА*\n\n"
        f"Ваш баланс: *{user_data.stars_balance} Telegram Stars*\n\n"
        f"💰 *Стоимость:*\n"
        f"• Фотография: {PRICE_PHOTO} ⭐\n"
        f"• Видео: {PRICE_VIDEO} ⭐",
        parse_mode='Markdown',
        reply_markup=markup
    )

# ========== ВЕРИФИКАЦИЯ ==========
@bot.message_handler(content_types=['photo', 'video', 'video_note'])
def handle_verification(message):
    """Обработка верификации"""
    user = message.from_user
    user_data = storage.get_user(user.id, user.username, user.first_name)
    
    if user_data.verified:
        # Если уже верифицирован, проверяем ожидает ли контент
        if user_data.pending_content:
            handle_paid_content(message, user_data)
        return
    
    # Определяем тип контента
    content_type = "фото" if message.photo else "видео" if message.video else "видеосообщение"
    
    # Верифицируем пользователя
    user_data.verified = True
    storage.update_user(user_data)
    
    storage.log(f"👤 @{user.username or user.id} → прошел верификацию ({content_type})")
    
    success_text = f"""
🎉 *ВЕРИФИКАЦИЯ ПРОЙДЕНА!*

Вы отправили {content_type} и теперь можете:
• Публиковать контент в канале
• Использовать систему Telegram Stars
• Пополнять баланс

💰 *Ваш стартовый баланс:* {user_data.stars_balance} ⭐

⚡ *Для публикации нажмите кнопку "📤 Опубликовать"*
"""
    
    bot.send_message(message.chat.id, success_text, parse_mode='Markdown')

# ========== ОБРАБОТКА КОЛБЕКОВ ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Обработка callback-запросов"""
    user = call.from_user
    user_data = storage.get_user(user.id, user.username, user.first_name)
    
    if call.data.startswith('buy_'):
        # Покупка звезд
        stars = int(call.data.replace('buy_', ''))
        show_payment_info(call, user_data, stars)
    
    elif call.data in ['publish_photo', 'publish_video']:
        # Выбор типа контента
        content_type = 'photo' if call.data == 'publish_photo' else 'video'
        price = PRICE_PHOTO if content_type == 'photo' else PRICE_VIDEO
        handle_content_selection(call, user_data, content_type, price)
    
    elif call.data == 'confirm_payment':
        # Подтверждение платежа (имитация)
        confirm_payment(call, user_data)
    
    elif call.data == 'cancel_payment':
        # Отмена платежа
        cancel_payment(call, user_data)

def show_payment_info(call, user_data, stars):
    """Показ информации о платеже"""
    amount_usd = stars / 100  # 1 звезда = $0.01
    
    payment_info = f"""
💳 *ИНФОРМАЦИЯ О ПЛАТЕЖЕ*

Пакет: *{stars} Telegram Stars*
Сумма: *${amount_usd:.2f}*

⚡ *Для настройки реальных платежей:*
1. Зарегистрируйтесь на stripe.com
2. Получите API ключи
3. Настройте в @BotFather
4. Используйте команду /addstars для теста

📚 Документация: core.telegram.org/bots/payments
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🌐 Настроить Stripe", url="https://stripe.com"),
        types.InlineKeyboardButton("📖 Документация", url="https://core.telegram.org/bots/payments")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=payment_info,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    storage.log(f"👤 @{user_data.username or user_data.user_id} → запросил покупку {stars} ⭐")

def handle_content_selection(call, user_data, content_type, price):
    """Обработка выбора типа контента"""
    content_name = "фотографию" if content_type == 'photo' else "видео"
    
    if user_data.stars_balance < price:
        bot.answer_callback_query(
            call.id,
            f"❌ Недостаточно звезд! Нужно {price} ⭐, у вас {user_data.stars_balance} ⭐",
            show_alert=True
        )
        return
    
    # Сохраняем выбор
    user_data.pending_content = {
        'type': content_type,
        'price': price,
        'message_id': call.message.message_id
    }
    storage.update_user(user_data)
    
    confirm_text = f"""
⚠️ *ПОДТВЕРЖДЕНИЕ ОПЛАТЫ*

Вы выбрали публикацию *{content_name}*
Стоимость: *{price} Telegram Stars*

Ваш баланс: {user_data.stars_balance} ⭐
После списания: {user_data.stars_balance - price} ⭐

✅ *Подтвердите оплату для продолжения*
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data='confirm_payment'),
        types.InlineKeyboardButton("❌ Отмена", callback_data='cancel_payment')
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=confirm_text,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    storage.log(f"👤 @{user_data.username or user_data.user_id} → выбрал {content_type} за {price} ⭐")

def confirm_payment(call, user_data):
    """Подтверждение платежа"""
    if not user_data.pending_content:
        bot.answer_callback_query(call.id, "❌ Ошибка: выбор не найден")
        return
    
    price = user_data.pending_content['price']
    content_type = user_data.pending_content['type']
    content_name = "фото" if content_type == 'photo' else "видео"
    
    # Списание звезд
    user_data.stars_balance -= price
    user_data.total_spent += price
    
    # Сохраняем что оплачено
    paid_content = user_data.pending_content.copy()
    user_data.pending_content = None
    storage.update_user(user_data)
    
    success_text = f"""
✅ *ОПЛАТА ПРОШЛА УСПЕШНО!*

Списано: {price} Telegram Stars
Осталось: {user_data.stars_balance} ⭐

Теперь отправьте {content_name} для публикации в канал.
"""
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=success_text,
        parse_mode='Markdown'
    )
    
    storage.log(f"👤 @{user_data.username or user_data.user_id} → оплатил {content_type} ({price} ⭐)")

def cancel_payment(call, user_data):
    """Отмена платежа"""
    user_data.pending_content = None
    storage.update_user(user_data)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ *Оплата отменена*",
        parse_mode='Markdown'
    )
    
    storage.log(f"👤 @{user_data.username or user_data.user_id} → отменил оплату")

def handle_paid_content(message, user_data):
    """Обработка оплаченного контента"""
    # В этой упрощенной версии просто публикуем в канал
    user = message.from_user
    
    try:
        caption = f"Автор: @{user.username if user.username else user.first_name}\nID: {user.id}"
        
        if message.photo:
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=caption)
            content_type = "фото"
        elif message.video:
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=caption)
            content_type = "видео"
        else:
            return
        
        bot.reply_to(message, f"✅ {content_type.capitalize()} успешно опубликовано в канале!")
        storage.log(f"👤 @{user.username or user.id} → опубликовал {content_type} в канал")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка публикации: {str(e)}")
        storage.log_error(f"Ошибка публикации: {e}")

# ========== АДМИНСКИЕ КОМАНДЫ ==========
@bot.message_handler(commands=['addstars'])
def add_stars_command(message):
    """Добавление звезд пользователю (админ)"""
    user = message.from_user
    
    # Список админов (добавьте свой ID)
    ADMINS = [123456789]  # Замените на ваш ID
    
    if user.id not in ADMINS:
        bot.reply_to(message, "❌ У вас нет прав администратора!")
        return
    
    try:
        # Формат: /addstars [user_id] [amount] или /addstars [amount] для себя
        args = message.text.split()
        
        if len(args) == 2:
            # Для себя: /addstars 1000
            target_id = user.id
            amount = int(args[1])
        elif len(args) == 3:
            # Для другого: /addstars 123456789 1000
            target_id = int(args[1])
            amount = int(args[2])
        else:
            bot.reply_to(message, "Использование:\n/addstars [количество]\n/addstars [user_id] [количество]")
            return
        
        target_user = storage.get_user(target_id)
        target_user.stars_balance += amount
        storage.update_user(target_user)
        
        bot.reply_to(message, f"✅ Пользователю {target_id} добавлено {amount} Telegram Stars!")
        
        # Уведомляем пользователя если он не админ
        if target_id != user.id:
            try:
                bot.send_message(
                    target_id,
                    f"💰 На ваш баланс зачислено {amount} Telegram Stars!\n\n"
                    f"Текущий баланс: {target_user.stars_balance} ⭐"
                )
            except:
                pass
        
        storage.log(f"👤 Админ @{user.username or user.id} → добавил {amount} ⭐ пользователю {target_id}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        storage.log_error(f"Ошибка команды addstars: {e}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Статистика бота"""
    user = message.from_user
    
    total_users = len(storage.users)
    verified_users = sum(1 for u in storage.users.values() if u.verified)
    total_stars = sum(u.stars_balance for u in storage.users.values())
    total_spent = sum(u.total_spent for u in storage.users.values())
    
    stats_text = f"""
📊 *СТАТИСТИКА БОТА*

👥 Пользователей: {total_users}
✅ Верифицировано: {verified_users}
⭐ Всего звезд в системе: {total_stars}
💰 Потрачено звезд: {total_spent}

⚡ *Топ 5 пользователей:*
"""
    
    # Сортируем по балансу
    top_users = sorted(storage.users.values(), key=lambda x: x.stars_balance, reverse=True)[:5]
    
    for i, user_data in enumerate(top_users, 1):
        name = user_data.first_name or f"ID:{user_data.user_id}"
        stats_text += f"{i}. {name}: {user_data.stars_balance} ⭐\n"
    
    bot.reply_to(message, stats_text, parse_mode='Markdown')
    storage.log(f"👤 @{user.username or user.id} → запросил статистику")

# ========== ЗАПУСК БОТА ==========
def main():
    """Основная функция запуска"""
    print("=" * 70)
    print("🤖 TELEGRAM CONTENT PUBLISHER BOT")
    print("=" * 70)
    print(f"Токен бота: ***{TOKEN[-10:]}")
    print(f"Канал публикации: {CHANNEL_ID}")
    print(f"Цена фото: {PRICE_PHOTO} Telegram Stars")
    print(f"Цена видео: {PRICE_VIDEO} Telegram Stars")
    print("=" * 70)
    print("🚀 Запуск бота...")
    print("=" * 70)
    
    # Пытаемся установить аватар
    set_bot_avatar()
    
    # Запускаем бота
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        storage.log_error(f"Ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка: {e}")

if __name__ == '__main__':
    main()