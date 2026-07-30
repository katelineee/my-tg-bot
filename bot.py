import os
import logging
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
- Никаких "ёмкостей", "расширений", "потоков" — говори прямо
- Будь конкретным, а не абстрактным
- НЕ ИСПОЛЬЗУЙ СЛОВО "ПАХОТА" — вместо него используй "выгорание" или "напряжение"

ПРИМЕРЫ УДАЧНЫХ ФРАЗ:
❌ "Моя емкость растет" → ✅ "Я спокойно принимаю любые деньги"
❌ "Финансовое расширение" → ✅ "У меня всегда есть столько, сколько нужно"
❌ "Внутреннее право" → ✅ "Я разрешаю себе получать больше"
❌ "Пахота" → ✅ "Выгорание" или "Напряжение"

ФОРМАТ ОТВЕТА (строго соблюдать):

🌟 КЛЮЧЕВАЯ МЫСЛЬ:
Одна простая фраза, которую можно запомнить.

🎯 МАНИФЕСТАЦИЯ:
Короткая фраза, которую можно повторять про себя или вслух.

✨ АФФИРМАЦИИ (7-10 штук):
Короткие, простые предложения.
Не больше 5-6 слов в каждой.
Чередуй эмодзи.

🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ:
3-4 самые сильные и простые фразы.

❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ:
Один простой вопрос, который включает тело и чувства.

💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ:
Одна фраза, которая остается в голове на весь день.

🔑 КЛЮЧЕВОЙ ВЫВОД:
Одна простая истина.

ГЛАВНОЕ ПРАВИЛО:
Если фразу можно сказать на кухне за чашкой чая — значит, она правильная.
"""

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Снять напряжение", callback_data="menu_ease_practice")],
        [InlineKeyboardButton("🧠 Разобрать Тревогу", callback_data="menu_mindset")],
        [InlineKeyboardButton("🗝️ Упражнение Мастер-Ключ", callback_data="menu_masterkey")]
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

# ============ ВАЖНО: ПРАВИЛЬНАЯ МОДЕЛЬ ============
def ask_ai(prompt_text):
    response = client.models.generate_content(
        model="gemini-3.6-flash",  # <--- ТОЛЬКО ЭТА МОДЕЛЬ! НЕ grok-beta
        contents=prompt_text,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 *Проводник по пересборке состояния*\n\n"
        "Привет. Я помогу тебе выйти из выгорания, тревоги и гиперконтроля.\n"
        "Выбери направление или просто напиши, что тебя беспокоит."
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

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await start(update, context)

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
            "🧠 *Напиши мне, что тебя сейчас ограничивает или тревожит.*\n\n"
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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🌟 Бот запущен!")
    app.run_polling(drop_pending_updates=True)
