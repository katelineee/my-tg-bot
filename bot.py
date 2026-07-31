import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from google import genai

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

SYSTEM_PROMPT = """
Ты — фундаментальный наставник по работе с мышлением, законами внимания, визуализации и метафизике реального присутствия.

ТВОЯ МЕТОДОЛОГИЧЕСКАЯ БАЗА:
1. Мастер-Ключ (Хенел): Внешний мир — зеркало внутреннего состояния.
2. Прикладная Метафизика (Костыль): Растождествление с выгоранием, переход в Авторство.
3. Невилл Годдард: "Feeling is the Secret", "Living from the End".
4. Джо Диспенза: Нейропластичность, эпигенетика.
5. Трансерфинг (Зеланд): Снятие важности, убирание блоков.
6. Карл Юнг: Интеграция тени, принятие себя.
7. Экхарт Толле: Сила Настоящего Момента.
8. Луиза Хей: Исцеление через прощение и аффирмации.
9. Грегг Брейден: Наука о сознании, наблюдатель создает событие.

ТВОЙ СТИЛЬ:
- Говори как мудрый друг
- Используй ПРОСТЫЕ слова
- НИКАКИХ "ёмкостей", "расширений", "потоков"
- НЕ ИСПОЛЬЗУЙ слово "пахота" — используй "выгорание" или "напряжение"

ФОРМАТ ОТВЕТА:
🌟 КЛЮЧЕВАЯ МЫСЛЬ
🎯 МАНИФЕСТАЦИЯ
✨ АФФИРМАЦИИ (8-10 штук)
🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ
❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ
💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ
🔑 КЛЮЧЕВОЙ ВЫВОД
"""

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Снять напряжение", callback_data="menu_ease_practice")],
        [InlineKeyboardButton("🧠 Разобрать тревогу", callback_data="menu_mindset")],
        [InlineKeyboardButton("🗝️ Мастер-Ключ: практика", callback_data="menu_masterkey")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manifest_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Финансы", callback_data="manifest_money"),
         InlineKeyboardButton("💼 Работа и дело", callback_data="manifest_career")],
        [InlineKeyboardButton("❤️ Отношения", callback_data="manifest_love"),
         InlineKeyboardButton("🤝 Дружба и поддержка", callback_data="manifest_friendship")],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 Семья", callback_data="manifest_family"),
         InlineKeyboardButton("✈️ Путешествия", callback_data="manifest_travel")],
        [InlineKeyboardButton("🏠 Дом и уют", callback_data="manifest_home"),
         InlineKeyboardButton("💪 Здоровье", callback_data="manifest_health")],
        [InlineKeyboardButton("🎨 Творчество", callback_data="manifest_creativity"),
         InlineKeyboardButton("🧘 Легкость и покой", callback_data="manifest_ease")],
        [InlineKeyboardButton("🦁 Харизма", callback_data="manifest_charisma"),
         InlineKeyboardButton("🔥 Уверенность", callback_data="manifest_confidence")],
        [InlineKeyboardButton("🧠 Ум и мудрость", callback_data="manifest_wisdom"),
         InlineKeyboardButton("😂 Чувство юмора", callback_data="manifest_humor")],
        [InlineKeyboardButton("😌 Внутренний покой", callback_data="manifest_inner_peace"),
         InlineKeyboardButton("🌸 Женственность", callback_data="manifest_femininity")],
        [InlineKeyboardButton("💎 Красота", callback_data="manifest_beauty"),
         InlineKeyboardButton("⚡ Энергетика", callback_data="manifest_energy")],
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌟 *Проводник по пересборке состояния*\n\nПривет. Я помогу тебе выйти из выгорания, тревоги и гиперконтроля.\nВыбери направление или просто напиши, что тебя беспокоит."
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await start(update, context)

    elif data == "menu_manifest":
        await query.message.edit_text("🎯 *Выбери тему для настройки:*\n\nЯ помогу тебе раскрыть любую сферу жизни.", parse_mode="Markdown", reply_markup=get_manifest_keyboard())

    elif data.startswith("manifest_"):
        theme_map = {
            "manifest_money": "Дай мощную манифестацию и аффирмации на деньги. Говори просто и сильно.",
            "manifest_career": "Дай мощную манифестацию и аффирмации на успех в работе.",
            "manifest_love": "Дай мощную манифестацию и аффирмации на отношения и любовь.",
            "manifest_friendship": "Дай мощную манифестацию и аффирмации на дружбу и поддержку.",
            "manifest_family": "Дай мощную манифестацию и аффирмации на семью.",
            "manifest_travel": "Дай мощную манифестацию и аффирмации на путешествия.",
            "manifest_home": "Дай мощную манифестацию и аффирмации на дом и уют.",
            "manifest_ease": "Дай мощную манифестацию и аффирмации на лёгкость и покой.",
            "manifest_health": "Дай мощную манифестацию и аффирмации на здоровье.",
            "manifest_creativity": "Дай мощную манифестацию и аффирмации на творчество.",
            "manifest_charisma": "Дай мощную манифестацию и аффирмации на харизму.",
            "manifest_wisdom": "Дай мощную манифестацию и аффирмации на ум и мудрость.",
            "manifest_humor": "Дай мощную манифестацию и аффирмации на лёгкость и юмор.",
            "manifest_confidence": "Дай мощную манифестацию и аффирмации на уверенность.",
            "manifest_inner_peace": "Дай мощную манифестацию и аффирмации на внутренний покой.",
            "manifest_beauty": "Дай мощную манифестацию и аффирмации на красоту.",
            "manifest_energy": "Дай мощную манифестацию и аффирмации на энергетику.",
            "manifest_femininity": "Дай мощную манифестацию и аффирмации на женственность."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию. Без слова 'пахота'. Говори мощно и прямо.")
        await query.message.edit_text("🎯 *Формирую мощную настройку...*", parse_mode="Markdown")
        try:
            reply = ask_ai(prompt)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Другая тема", callback_data="menu_manifest")], [InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]])
            await query.message.edit_text(reply, parse_mode="Markdown", reply_markup=keyboard)
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_visualize":
        await query.message.edit_text("👁️ *Готовлю визуализацию...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай мощную технику визуализации по Невиллу Годдарду. Говори просто и сильно.")
            await query.message.edit_text(reply, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]]))
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_ease_practice":
        await query.message.edit_text("🌿 *Разбираем напряжение...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай упражнение и аффирмации от выгорания. Говори просто и сильно.")
            await query.message.edit_text(reply, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]]))
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_mindset":
        await query.message.edit_text("🧠 *Напиши мне, что тебя сейчас ограничивает или тревожит.*\n\nЯ разберу это через Мастер-Ключ и дам мощные аффирмации.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]]))

    elif data == "menu_masterkey":
        await query.message.edit_text("🗝️ *Формирую практику Мастер-Ключ...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай мощную практику из Мастер-Ключа. Говори прямо и сильно.")
            await query.message.edit_text(reply, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]]))
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = ask_ai(f"Пользователь пишет: \"{user_text}\"\nРазбери через Мастер-Ключ, Годдарда и метафизику. Дай мощные аффирмации. Говори прямо.")
        await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📱 Главное меню", callback_data="menu_main")]]))
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🌟 Бот запущен!")
    app.run_polling(drop_pending_updates=True)
