import os
import logging
import json
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, CallbackContext
)
from google import genai

# ============ НАСТРОЙКИ ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Ошибка: Не найдены переменные окружения TELEGRAM_BOT_TOKEN или GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# ============ ХРАНЕНИЕ ПОДПИСЧИКОВ ============
SUBSCRIBERS_FILE = "subscribers.json"

def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            data = json.load(f)
            return set(data) if isinstance(data, list) else set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_subscribers(subscribers):
    try:
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(list(subscribers), f)
    except Exception as e:
        logging.error(f"Ошибка сохранения подписчиков: {e}")

user_ids = load_subscribers()

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """
Ты — фундаментальный наставник по работе с мышлением, законами внимания, визуализации и метафизике реального присутствия.

ТВОЯ МЕТОДОЛОГИЧЕСКАЯ БАЗА:
1. «Система Мастер-Ключ» (Чарльз Хенел): Внешний мир — точное отражение ментальной причины. Меняешь ментальный образ — меняется материя.
2. Проводник Алины Костыль & Прикладная Метафизика:
   - Растождествление с выгоранием, режимом "пахоты", гиперконтролем и чувством долга.
   - Выявление скрытых выгод сидеть в тревоге или нехватке.
   - Перевод из дефицита в состояние Авторства и Внутреннего Права.
3. Невилл Годдард & Джо Диспенза:
   - Принцип "Feeling is the Secret" и "Living from the End".
4. Снятие важности (Трансерфинг): Убирание судорожной цепкости.

ТВОИ ИНСТРУМЕНТЫ:
- Давать емкие, глубокие аффирмации и манифестации БЕЗ пустой воды.
- Задавать глубокие вопросы для ведения пользователя по визуализации.
- Общаться как мудрый соратник и метафизический коуч.

ФОРМАТ ОТВЕТА (строго соблюдать):

🌟 КЛЮЧЕВАЯ МЫСЛЬ:
Одно-два предложения, задающие тон.

🎯 МАНИФЕСТАЦИЯ:
Короткая, мощная формулировка для чтения вслух.
Используй *звездочки* для выделения ключевых слов.

✨ АФФИРМАЦИИ (минимум 5-7 штук):
Каждая с новой строки.
Короткие, ритмичные, запоминающиеся.
Чередуй с разными эмодзи для визуального разнообразия.

🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ:
3-4 самые сильные аффирмации, выделенные отдельно.

❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ:
1 глубокий вопрос для размышления.

💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ:
Мощная фраза для запоминания на день.

🔑 КЛЮЧЕВОЙ ВЫВОД:
Одна фраза для повторения в течение дня.

ВАЖНО:
- Используй РАЗНЫЕ ЭМОДЗИ для визуального разнообразия
- Аффирмации должны быть КОРОТКИМИ (4-7 слов)
- Общий объем: 15-20 строк
- Текст должен быть РИТМИЧНЫМ для легкого запоминания
"""

# ============ КЛАВИАТУРЫ ============
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Сбросить Пахоту", callback_data="menu_ease_practice")],
        [InlineKeyboardButton("🧠 Разобрать Тревогу", callback_data="menu_mindset")],
        [InlineKeyboardButton("🗝️ Упражнение Мастер-Ключ", callback_data="menu_masterkey")],
        [InlineKeyboardButton("📅 Ежедневные настройки", callback_data="menu_daily")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manifest_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Финансы", callback_data="manifest_money")],
        [InlineKeyboardButton("🌿 Легкость", callback_data="manifest_ease")],
        [InlineKeyboardButton("🚀 Масштаб", callback_data="manifest_career")],
        [InlineKeyboardButton("❤️ Самоценность", callback_data="manifest_worth")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ ФУНКЦИИ AI ============
def ask_ai(prompt_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt_text,
            config={"system_instruction": SYSTEM_PROMPT}
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка Gemini API: {e}")
        return "⚠️ Извините, произошла ошибка при обращении к AI. Попробуйте позже."

def get_morning_affirmation():
    prompt = """
    Создай мощную утреннюю настройку на день.
    Включи:
    1. 🌅 Приветствие нового дня
    2. 🎯 Основной фокус дня
    3. ✨ 5-7 аффирмаций для начала дня
    4. 🔑 Ключевая фраза дня для повторения
    5. ❓ Вопрос для размышления
    Используй яркие эмодзи, сделай текст вдохновляющим.
    """
    return ask_ai(prompt)

def get_evening_reflection():
    prompt = """
    Создай вечернюю практику благодарности и пересборки.
    Включи:
    1. 🌙 Приветствие завершению дня
    2. 🙏 5 аффирмаций благодарности
    3. ✨ Фокус на том, что получилось
    4. 🌈 Перепрограммирование негатива
    5. 💫 Настройка на завтрашний день
    Используй яркие эмодзи.
    """
    return ask_ai(prompt)

def get_random_affirmation():
    prompt = """
    Дай случайную мощную аффирмацию дня.
    1. 🔥 Ключевая аффирмация
    2. ✨ 3-5 поддерживающих аффирмаций
    3. 💡 Инсайт для размышления
    """
    return ask_ai(prompt)

# ============ КОМАНДЫ ============
def start(update: Update, context: CallbackContext):
    text = (
        "🌟 *Проводник по пересборке состояния*\n\n"
        "Привет! Я помогу тебе выйти из пахоты, тревоги и гиперконтроля.\n\n"
        "📌 *Мои возможности:*\n"
        "✨ Настройки и манифестации\n"
        "👁️ Практики визуализации\n"
        "🌿 Снятие пахоты и тревоги\n"
        "🗝️ Упражнения из Мастер-Ключа\n\n"
        "🔥 *Ежедневная поддержка:*\n"
        "🌅 Утренняя настройка в 8:00\n"
        "🌙 Вечерняя рефлексия в 21:00\n"
        "🎲 Случайная аффирмация: /random\n\n"
        "💡 Подпишись на ежедневные настройки: /subscribe\n"
        "🚫 Отписаться: /unsubscribe"
    )
    
    update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

def subscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_ids.add(user_id)
    save_subscribers(user_ids)
    
    update.message.reply_text(
        "✅ *Ты подписан на ежедневные настройки!*\n\n"
        "🌅 В 8:00 я буду присылать утреннюю настройку.\n"
        "🌙 В 21:00 я буду присылать вечернюю рефлексию.\n\n"
        "💡 /random - случайная аффирмация\n"
        "🚫 /unsubscribe - отписаться",
        parse_mode="Markdown"
    )

def unsubscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        save_subscribers(user_ids)
    
    update.message.reply_text(
        "❌ Ты отписан от ежедневных рассылок.\n\n"
        "💡 /subscribe - подписаться снова",
        parse_mode="Markdown"
    )

def random_affirmation(update: Update, context: CallbackContext):
    update.message.reply_text("🎲 *Генерирую случайную аффирмацию...*", parse_mode="Markdown")
    try:
        reply = get_random_affirmation()
        update.message.reply_text(
            reply,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Еще одну", callback_data="random_affirmation")],
                [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
            ])
        )
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")

# ============ РАССЫЛКИ ============
def send_daily_affirmations(context: CallbackContext):
    if not user_ids:
        return
    
    morning_text = get_morning_affirmation()
    
    for user_id in list(user_ids):
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=f"🌅 *ДОБРОЕ УТРО! НАСТРОЙКА НА ДЕНЬ*\n\n{morning_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📱 Открыть меню", callback_data="menu_main")],
                    [InlineKeyboardButton("🔄 Обновить", callback_data="refresh_morning")]
                ])
            )
        except Exception as e:
            if "bot was blocked" in str(e) or "user is deactivated" in str(e):
                user_ids.discard(user_id)
                save_subscribers(user_ids)
            else:
                logging.error(f"Ошибка отправки пользователю {user_id}: {e}")

def send_evening_reflection(context: CallbackContext):
    if not user_ids:
        return
    
    evening_text = get_evening_reflection()
    
    for user_id in list(user_ids):
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=f"🌙 *ВЕЧЕРНЯЯ РЕФЛЕКСИЯ*\n\n{evening_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📱 Открыть меню", callback_data="menu_main")],
                    [InlineKeyboardButton("🔄 Обновить", callback_data="refresh_evening")]
                ])
            )
        except Exception as e:
            if "bot was blocked" in str(e) or "user is deactivated" in str(e):
                user_ids.discard(user_id)
                save_subscribers(user_ids)
            else:
                logging.error(f"Ошибка отправки пользователю {user_id}: {e}")

# ============ ОБРАБОТЧИК КНОПОК ============
def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "menu_main":
        text = (
            "🌟 *Проводник по пересборке состояния*\n\n"
            "Привет! Я помогу тебе выйти из пахоты, тревоги и гиперконтроля.\n\n"
            "📌 *Мои возможности:*\n"
            "✨ Настройки и манифестации\n"
            "👁️ Практики визуализации\n"
            "🌿 Снятие пахоты и тревоги\n"
            "🗝️ Упражнения из Мастер-Ключа\n\n"
            "🔥 *Ежедневная поддержка:*\n"
            "🌅 Утренняя настройка в 8:00\n"
            "🌙 Вечерняя рефлексия в 21:00\n"
            "🎲 Случайная аффирмация: /random\n\n"
            "💡 Подпишись на ежедневные настройки: /subscribe\n"
            "🚫 Отписаться: /unsubscribe"
        )
        query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    elif data == "menu_daily":
        query.message.edit_text(
            "📅 *Ежедневные настройки*\n\n"
            "🌅 Утро: настройка на день в 8:00\n"
            "🌙 Вечер: рефлексия в 21:00\n\n"
            "💡 Подпишись, чтобы получать их автоматически!\n"
            "Используй /subscribe или /unsubscribe",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Подписаться", callback_data="subscribe_now")],
                [InlineKeyboardButton("🚫 Отписаться", callback_data="unsubscribe_now")],
                [InlineKeyboardButton("🔙 В меню", callback_data="menu_main")]
            ])
        )
    
    elif data == "subscribe_now":
        user_id = update.effective_user.id
        user_ids.add(user_id)
        save_subscribers(user_ids)
        query.message.edit_text(
            "✅ *Ты подписан на ежедневные настройки!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В меню", callback_data="menu_main")]
            ])
        )
    
    elif data == "unsubscribe_now":
        user_id = update.effective_user.id
        if user_id in user_ids:
            user_ids.remove(user_id)
            save_subscribers(user_ids)
        query.message.edit_text(
            "❌ *Ты отписан от рассылок*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В меню", callback_data="menu_main")]
            ])
        )
    
    elif data == "random_affirmation":
        try:
            reply = get_random_affirmation()
            query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще одну", callback_data="random_affirmation")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")
    
    elif data == "refresh_morning":
        try:
            reply = get_morning_affirmation()
            query.message.edit_text(
                f"🌅 *ОБНОВЛЕННАЯ НАСТРОЙКА*\n\n{reply}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще раз", callback_data="refresh_morning")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")
    
    elif data == "refresh_evening":
        try:
            reply = get_evening_reflection()
            query.message.edit_text(
                f"🌙 *ОБНОВЛЕННАЯ РЕФЛЕКСИЯ*\n\n{reply}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще раз", callback_data="refresh_evening")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")
    
    elif data == "menu_manifest":
        query.message.edit_text(
            "🎯 *Выбери тему для настройки:*",
            parse_mode="Markdown",
            reply_markup=get_manifest_keyboard()
        )

    elif data.startswith("manifest_"):
        theme_map = {
            "manifest_money": "Дай яркую манифестацию на финансовое расширение с 7-10 аффирмациями. Используй эмодзи для запоминания. Сделай текст ритмичным для повторения.",
            "manifest_ease": "Дай настройку на отпускание гиперконтроля. 7-10 аффирмаций. Яркие эмодзи.",
            "manifest_career": "Дай манифестацию на масштаб и проявленность. 7-10 аффирмаций.",
            "manifest_worth": "Дай манифестацию на самоценность. 7-10 аффирмаций."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию.")
        
        query.message.edit_text("🎯 *Формирую мощную настройку...*", parse_mode="Markdown")
        
        try:
            reply = ask_ai(prompt)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Обновить", callback_data=data)],
                [InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]
            ])
            query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_visualize":
        query.message.edit_text("👁️ *Готовлю визуализацию...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай технику визуализации по Невиллу Годдарду. Добавь яркие эмодзи и аффирмации для визуализации.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_ease_practice":
        query.message.edit_text("🌿 *Разбираем пахоту...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Объясни, почему пахота противоречит метафизике. Дай упражнение и 5 аффирмаций для снятия. Яркие эмодзи.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_mindset":
        query.message.edit_text(
            "🧠 *Напиши мне, что тебя сейчас ограничивает.*\n\n"
            "Я дам аффирмации для перепрограммирования.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]
            ])
        )

    elif data == "menu_masterkey":
        query.message.edit_text("🗝️ *Формирую упражнение...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай упражнение из Мастер-Ключа с аффирмациями для закрепления. Яркие эмодзи.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            query.message.edit_text(f"❌ Ошибка: {e}")

# ============ ОБРАБОТЧИК СООБЩЕНИЙ ============
def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        reply = ask_ai(
            f"Пользователь пишет: \"{user_text}\"\n"
            "Разбери мысль через метафизику. Дай яркие аффирмации для перепрограммирования. Минимум 7 аффирмаций."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Главное меню", callback_data="menu_main")]
        ])
        update.message.reply_text(
            reply,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")

# ============ ЗАПУСК ============
if __name__ == '__main__':
    try:
        updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Добавляем обработчики
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("subscribe", subscribe))
        dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
        dp.add_handler(CommandHandler("random", random_affirmation))
        
        dp.add_handler(CallbackQueryHandler(button_click))
        dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Настраиваем ежедневные рассылки
        jq = updater.job_queue
        
        if jq:
            jq.run_daily(
                send_daily_affirmations,
                time=time(hour=8, minute=0, second=0)
            )
            jq.run_daily(
                send_evening_reflection,
                time=time(hour=21, minute=0, second=0)
            )
            
            print("🌟 Бот запущен с ежедневными настройками!")
            print(f"📊 Подписчиков: {len(user_ids)}")
            print("🌅 Утренняя рассылка в 8:00")
            print("🌙 Вечерняя рассылка в 21:00")
        else:
            print("⚠️ JobQueue не доступна. Ежедневные рассылки не будут работать.")
        
        print("🤖 Бот готов к работе!")
        
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        raise
