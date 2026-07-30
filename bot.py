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
"""

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации (с вопросами)", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Сбросить «Пахоту» и Гиперконтроль", callback_data="menu_ease_practice")],
        [InlineKeyboardButton("🧠 Разобрать затык / тревогу", callback_data="menu_mindset")],
        [InlineKeyboardButton("🗝️ Упражнение из «Мастер-Ключа»", callback_data="menu_masterkey")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manifest_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Финансы & Входящий поток", callback_data="manifest_money")],
        [InlineKeyboardButton("🌿 Состояние & Легкое позволение", callback_data="manifest_ease")],
        [InlineKeyboardButton("🚀 Проявленность & Масштаб", callback_data="manifest_career")],
        [InlineKeyboardButton("❤️ Самоценность & Внутреннее право", callback_data="manifest_worth")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def ask_ai(prompt_text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет. Я твой проводник по пересборке состояния, законам внимания и визуализации.\n\n"
        "Выбери направление ниже или просто напиши, что тебя сейчас тревожит."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=get_main_keyboard())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await start(update, context)

    elif data == "menu_manifest":
        await query.message.edit_text(
            "Выбери тему для настройки фокуса внимания и формирования точной манифестации:",
            reply_markup=get_manifest_keyboard()
        )

    elif data.startswith("manifest_"):
        theme_map = {
            "manifest_money": "Дай точечную манифестацию и аффирмации на финансовое расширение БЕЗ пахоты и тревоги.",
            "manifest_ease": "Дай настройку на отпускание гиперконтроля и отработок.",
            "manifest_career": "Дай манифестацию на масштаб и проявленность из состояния внутреннего авторитета.",
            "manifest_worth": "Дай манифестацию на безусловную самоценность."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию.")
        await query.message.edit_text("Формирую настройку...")
        try:
            reply = ask_ai(prompt)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(reply, reply_markup=keyboard)
        except Exception as e:
            await query.message.edit_text(f"Ошибка: {e}")

    elif data == "menu_visualize":
        await query.message.edit_text("Готовлю пошаговый проводник визуализации...")
        try:
            reply = ask_ai("Дай короткую технику визуализации по Невиллу Годдарду и 3 сенсорных вопроса пользователю.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(reply, reply_markup=keyboard)
        except Exception as e:
            await query.message.edit_text(f"Ошибка: {e}")

    elif data == "menu_ease_practice":
        await query.message.edit_text("Разбираем состояние пахоты...")
        try:
            reply = ask_ai("Объясни, почему 'пахота' противоречит метафизике Хенела и дай 1 телесное упражнение.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(reply, reply_markup=keyboard)
        except Exception as e:
            await query.message.edit_text(f"Ошибка: {e}")

    elif data == "menu_mindset":
        await query.message.edit_text(
            "Напиши мне сообщением то, что тебя сейчас ограничивает или тревожит.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]])
        )

    elif data == "menu_masterkey":
        await query.message.edit_text("Формирую упражнение из «Мастер-Ключа»...")
        try:
            reply = ask_ai("Дай 1 практическое упражнение из книги 'Система Мастер-Ключ' Чарльза Хенела.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(reply, reply_markup=keyboard)
        except Exception as e:
            await query.message.edit_text(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = ask_ai(f"Пользователь пишет: \"{user_text}\"\nРазбери мысль через 'Мастер-Ключ', Годдарда и метафизику Алины Костыль.")
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 Главное меню", callback_data="menu_main")]])
        await update.message.reply_text(reply, reply_markup=keyboard)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот успешно запущен на Render (Gemini)!")
    app.run_polling(drop_pending_updates=True)
