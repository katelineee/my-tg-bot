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

# ОБНОВЛЕННЫЙ SYSTEM_PROMPT - яркий формат с аффирмациями
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

1. 🌟 КЛЮЧЕВАЯ МЫСЛЬ:
   Одно-два предложения, задающие тон.

2. 🎯 МАНИФЕСТАЦИЯ (жирным текстом):
   Короткая, мощная формулировка для чтения вслух.
   Используй *звездочки* для выделения ключевых слов.

3. ✨ АФФИРМАЦИИ (минимум 5-7 штук):
   Каждая с новой строки.
   Короткие, ритмичные, запоминающиеся.
   Чередуй с разными эмодзи для визуального разнообразия.

4. 🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ:
   3-4 самые сильные аффирмации, выделенные отдельно.

5. ❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ:
   1 глубокий вопрос для размышления.

6. 💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ:
   Мощная фраза для запоминания на день.

7. 🔑 КЛЮЧЕВОЙ ВЫВОД:
   Одна фраза для повторения в течение дня.

ВАЖНО:
- Используй РАЗНЫЕ ЭМОДЗИ для визуального разнообразия
- Аффирмации должны быть КОРОТКИМИ (4-7 слов)
- Общий объем: 15-20 строк
- Текст должен быть РИТМИЧНЫМ для легкого запоминания
"""

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Сбросить Пахоту", callback_data="menu_ease_practice")],
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

def ask_ai(prompt_text):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_text,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 *Проводник по пересборке состояния*\n\n"
        "Привет. Я помогу тебе выйти из пахоты, тревоги и гиперконтроля.\n"
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
            "manifest_money": "Дай яркую манифестацию на финансовое расширение с 7-10 аффирмациями. Используй эмодзи для запоминания. Сделай текст ритмичным для повторения.",
            "manifest_ease": "Дай настройку на отпускание гиперконтроля. 7-10 аффирмаций. Яркие эмодзи.",
            "manifest_career": "Дай манифестацию на масштаб и проявленность. 7-10 аффирмаций.",
            "manifest_worth": "Дай манифестацию на самоценность. 7-10 аффирмаций."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию.")
        
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
            reply = ask_ai("Дай технику визуализации по Невиллу Годдарду. Добавь яркие эмодзи и аффирмации для визуализации.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📱 В главное меню", callback_data="menu_main")]])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

    elif data == "menu_ease_practice":
        await query.message.edit_text("🌿 *Разбираем пахоту...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Объясни, почему пахота противоречит метафизике. Дай упражнение и 5 аффирмаций для снятия. Яркие эмодзи.")
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
            reply = ask_ai("Дай упражнение из Мастер-Ключа с аффирмациями для закрепления. Яркие эмодзи.")
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
            "Разбери мысль через метафизику. Дай яркие аффирмации для перепрограммирования. Минимум 7 аффирмаций."
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
    
    print("🌟 Бот запущен с ярким форматом!")
    app.run_polling(drop_pending_updates=True)
