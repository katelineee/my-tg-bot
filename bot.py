import os
import logging
import json
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from google import genai

# Ключи подтягиваются из защищенных настроек Render (Environment Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Инициализируем клиента Gemini
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

# ============ ОБНОВЛЕННЫЙ SYSTEM_PROMPT ============
SYSTEM_PROMPT = """
Ты — фундаментальный наставник по работе с мышлением, законами внимания, визуализации и метафизике реального присутствия.

ТВОЯ МЕТОДОЛОГИЧЕСКАЯ БАЗА:
1. «Система Мастер-Ключ» (Чарльз Хенел): Внешний мир — точное отражение ментальной причины. Меняешь ментальный образ — меняется материя.
2. Проводник Алины Костыль & Прикладная Метафизика:
   - Растождествление с выгоранием, гиперконтролем и чувством долга.
   - Выявление скрытых выгод сидеть в тревоге или нехватке.
   - Перевод из дефицита в состояние Авторства и Внутреннего Права.
3. Невилл Годдард & Джо Диспенза:
   - Принцип "Feeling is the Secret" и "Living from the End".
4. Снятие важности (Трансерфинг): Убирание судорожной цепкости.

ТВОЙ СТИЛЬ ОБЩЕНИЯ:
- Говори как мудрый друг, который прошел через это сам
- Используй ПРОСТЫЕ, ЗЕМНЫЕ СЛОВА, которые понятны каждому
- НИКАКИХ "ЁМКОСТЕЙ", "РАСШИРЕНИЙ", "ПОТОКОВ" — говори прямо
- НЕ ИСПОЛЬЗУЙ СЛОВО "ПАХОТА" — используй "выгорание" или "напряжение"
- Используй метафоры из жизни: "как дышать", "как пить воду"
- Будь конкретным, а не абстрактным

ПРИМЕРЫ УДАЧНЫХ ФРАЗ вместо абстракций:
❌ "Моя емкость растет" → ✅ "Я спокойно принимаю любые деньги"
❌ "Финансовое расширение" → ✅ "У меня всегда есть столько, сколько нужно"
❌ "Внутреннее право" → ✅ "Я разрешаю себе получать больше"
❌ "Пахота" → ✅ "Выгорание" или "Напряжение"
❌ "Материя подстраивается" → ✅ "Жизнь приносит мне то, что я хочу"
❌ "Состояние присутствия" → ✅ "Я чувствую себя уверенно и спокойно"

ФОРМАТ ОТВЕТА (строго соблюдать):

🌟 КЛЮЧЕВАЯ МЫСЛЬ:
Одна простая фраза, которую можно запомнить.
Говори как есть, без прикрас.

🎯 МАНИФЕСТАЦИЯ:
Короткая фраза, которую можно повторять про себя или вслух.
Пусть она звучит как факт, а не как желание.

✨ АФФИРМАЦИИ (7-10 штук):
Короткие, простые предложения.
Каждая начинается с "Я" или безличная.
Не больше 5-6 слов в каждой.
Чередуй эмодзи.

🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ:
3-4 самые сильные и простые фразы.
Те, которые хочется повторять в течение дня.

❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ:
Один простой вопрос, который включает тело и чувства.
Не абстрактный, а живой.

💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ:
Одна фраза, которая остается в голове на весь день.

🔑 КЛЮЧЕВОЙ ВЫВОД:
То, что действительно важно запомнить.
Одна простая истина.

ГЛАВНОЕ ПРАВИЛО:
Если фразу можно сказать на кухне за чашкой чая — значит, она правильная.
Если фраза звучит как из книги по эзотерике — переформулируй.
"""

# ============ ФУНКЦИИ ДЛЯ ЕЖЕДНЕВНЫХ НАСТРОЕК ============
def get_morning_affirmation():
    prompt = """
    Создай мощную утреннюю настройку на день.
    Говори простым языком, как живой человек.
    Без слова "пахота". Используй "выгорание" или "напряжение".
    Включи:
    1. 🌅 Приветствие нового дня
    2. 🎯 Основной фокус дня
    3. ✨ 5-7 аффирмаций для начала дня
    4. 🔑 Ключевая фраза дня для повторения
    5. ❓ Вопрос для размышления
    Используй яркие эмодзи.
    """
    return ask_ai(prompt)

def get_evening_reflection():
    prompt = """
    Создай вечернюю практику благодарности и пересборки.
    Говори просто и тепло, как вечерний разговор.
    Без слова "пахота".
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
    Говори простым языком.
    Без слова "пахота".
    1. 🔥 Ключевая аффирмация
    2. ✨ 3-5 поддерживающих аффирмаций
    3. 💡 Инсайт для размышления
    """
    return ask_ai(prompt)

# ============ ОСНОВНЫЕ ФУНКЦИИ ============
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Снять напряжение", callback_data="menu_ease_practice")],
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

def ask_ai(prompt_text):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_text,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    return response.text

# ============ КОМАНДЫ ПОДПИСКИ ============
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_ids.add(user_id)
    save_subscribers(user_ids)
    
    await update.message.reply_text(
        "✅ *Ты подписан на ежедневные настройки!*\n\n"
        "🌅 В 8:00 я буду присылать утреннюю настройку.\n"
        "🌙 В 21:00 я буду присылать вечернюю рефлексию.\n\n"
        "💡 /random - случайная аффирмация\n"
        "🚫 /unsubscribe - отписаться",
        parse_mode="Markdown"
    )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        save_subscribers(user_ids)
    
    await update.message.reply_text(
        "❌ Ты отписан от ежедневных рассылок.\n\n"
        "💡 /subscribe - подписаться снова",
        parse_mode="Markdown"
    )

async def random_affirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎲 *Генерирую случайную аффирмацию...*", parse_mode="Markdown")
    try:
        reply = get_random_affirmation()
        await update.message.reply_text(
            reply,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Еще одну", callback_data="random_affirmation")],
                [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
            ])
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# ============ ФУНКЦИИ РАССЫЛОК ============
async def send_daily_affirmations(context: ContextTypes.DEFAULT_TYPE):
    """Утренняя рассылка"""
    if not user_ids:
        return
    
    morning_text = get_morning_affirmation()
    
    for user_id in list(user_ids):
        try:
            await context.bot.send_message(
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

async def send_evening_reflection(context: ContextTypes.DEFAULT_TYPE):
    """Вечерняя рассылка"""
    if not user_ids:
        return
    
    evening_text = get_evening_reflection()
    
    for user_id in list(user_ids):
        try:
            await context.bot.send_message(
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

# ============ ОБРАБОТЧИК КНОПОК ============
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await start(update, context)

    elif data == "menu_daily":
        await query.message.edit_text(
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
        await query.message.edit_text(
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
        await query.message.edit_text(
            "❌ *Ты отписан от рассылок*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В меню", callback_data="menu_main")]
            ])
        )

    elif data == "random_affirmation":
        try:
            reply = get_random_affirmation()
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще одну", callback_data="random_affirmation")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "refresh_morning":
        try:
            reply = get_morning_affirmation()
            await query.message.edit_text(
                f"🌅 *ОБНОВЛЕННАЯ НАСТРОЙКА*\n\n{reply}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще раз", callback_data="refresh_morning")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "refresh_evening":
        try:
            reply = get_evening_reflection()
            await query.message.edit_text(
                f"🌙 *ОБНОВЛЕННАЯ РЕФЛЕКСИЯ*\n\n{reply}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Еще раз", callback_data="refresh_evening")],
                    [InlineKeyboardButton("📱 В меню", callback_data="menu_main")]
                ])
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    # ============ ОСТАЛЬНЫЕ ОБРАБОТЧИКИ ============
    elif data == "menu_manifest":
        await query.message.edit_text(
            "🎯 *Выбери тему для настройки:*",
            parse_mode="Markdown",
            reply_markup=get_manifest_keyboard()
        )

    elif data.startswith("manifest_"):
        theme_map = {
            "manifest_money": "Дай яркую манифестацию на финансовое расширение с 7-10 аффирмациями. Говори простым языком, без абстракций. Без слова 'пахота'.",
            "manifest_ease": "Дай настройку на отпускание гиперконтроля. 7-10 аффирмаций. Простой язык. Без 'пахоты'.",
            "manifest_career": "Дай манифестацию на масштаб и проявленность. 7-10 аффирмаций. Простой язык. Без 'пахоты'.",
            "manifest_worth": "Дай манифестацию на самоценность. 7-10 аффирмаций. Простой язык. Без 'пахоты'."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию. Без слова 'пахота'.")
        
        await query.message.edit_text("🎯 *Формирую мощную настройку...*", parse_mode="Markdown")
        
        try:
            reply = ask_ai(prompt)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Обновить", callback_data=data)],
                [InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]
            ])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_visualize":
        await query.message.edit_text("👁️ *Готовлю визуализацию...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай технику визуализации по Невиллу Годдарду. Добавь яркие эмодзи и аффирмации для визуализации. Говори простым языком. Без слова 'пахота'.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_ease_practice":
        await query.message.edit_text("🌿 *Разбираем напряжение...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Объясни, как выгорание и гиперконтроль мешают жить. Дай упражнение и 5 аффирмаций для расслабления. Яркие эмодзи. Говори простым языком. Без слова 'пахота'. Вместо 'пахоты' используй 'напряжение' или 'выгорание'.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_mindset":
        await query.message.edit_text(
            "🧠 *Напиши мне, что тебя сейчас ограничивает.*\n\n"
            "Я дам аффирмации для перепрограммирования.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]
            ])
        )

    elif data == "menu_masterkey":
        await query.message.edit_text("🗝️ *Формирую упражнение...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай упражнение из Мастер-Ключа с аффирмациями для закрепления. Яркие эмодзи. Говори простым языком. Без слова 'пахота'.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

# ============ ОБРАБОТЧИК СООБЩЕНИЙ ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 *Проводник по пересборке состояния*\n\n"
        "Привет. Я помогу тебе выйти из выгорания, тревоги и гиперконтроля.\n"
        "Выбери направление или просто напиши, что тебя беспокоит.\n\n"
        "📌 *Доступные команды:*\n"
        "/subscribe - подписаться на ежедневные настройки\n"
        "/unsubscribe - отписаться от рассылок\n"
        "/random - случайная аффирмация"
    )
    if update.message:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        reply = ask_ai(
            f"Пользователь пишет: \"{user_text}\"\n"
            "Разбери мысль через метафизику. Дай яркие аффирмации для перепрограммирования. Минимум 7 аффирмаций. Говори простым языком, без абстракций. Без слова 'пахота'."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Главное меню", callback_data="menu_main")]
        ])
        await update.message.reply_text(
            reply,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# ============ ЗАПУСК ============
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("random", random_affirmation))
    
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    job_queue = app.job_queue
    
    if job_queue:
        job_queue.run_daily(
            send_daily_affirmations,
            time=time(hour=8, minute=0, second=0)
        )
        
        job_queue.run_daily(
            send_evening_reflection,
            time=time(hour=21, minute=0, second=0)
        )
        
        print("🌟 Бот запущен с ежедневными настройками!")
        print(f"📊 Подписчиков: {len(user_ids)}")
        print("🌅 Утренняя рассылка в 8:00")
        print("🌙 Вечерняя рассылка в 21:00")
    else:
        print("⚠️ JobQueue не доступна. Ежедневные рассылки не будут работать.")
    
    print("🌟 Бот запущен с ярким форматом!")
    app.run_polling(drop_pending_updates=True)
