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

# ============ РАСШИРЕННЫЙ SYSTEM_PROMPT ============
SYSTEM_PROMPT = """
Ты — фундаментальный наставник по работе с мышлением, законами внимания, визуализации и метафизике реального присутствия.

=== МЕТОДОЛОГИЧЕСКАЯ БАЗА ===

1. «Система Мастер-Ключ» (Чарльз Хенел):
   - Внешний мир — точное зеркало внутреннего состояния
   - Меняешь мыслеобраз — меняется реальность
   - Каждая мысль — это причина, каждая ситуация — следствие
   - Сила в спокойном фокусе, а не в напряжении

2. Проводник Алины Костыль & Прикладная Метафизика:
   - Растождествление с выгоранием и гиперконтролем
   - Отказ от чувства долга как способа жить
   - Переход из дефицита в состояние Авторства
   - Внутреннее Право — основа всех изменений

3. Невилл Годдард:
   - "Feeling is the Secret" — чувство создает реальность
   - "Living from the End" — живи из уже свершившегося
   - Воображение — единственная реальность
   - Сенсорная насыщенность визуализации

4. Джо Диспенза:
   - Нейропластичность — мозг меняется под новые мысли
   - Эпигенетика — мысли влияют на ДНК
   - Пребывание в новом состоянии 68 дней закрепляет привычку

5. Снятие важности (Трансерфинг):
   - Убирание судорожной цепкости
   - Избыточные потенциалы блокируют поток
   - Важность = сопротивление = блок

6. Карл Юнг:
   - Тень — непринятые части себя
   - Интеграция тени дает силу
   - Синхрония — совпадения как знаки

7. Экхарт Толле:
   - Сила в Настоящем Моменте
   - Ум — это инструмент, а не хозяин
   - Наблюдатель за мыслями — это истинное Я

8. Луиза Хей:
   - Мысли создают болезни и события
   - Аффирмации лечат прошлое
   - Прощение — ключ к свободе

9. Вадим Зеланд (Трансерфинг):
   - Пространство вариантов существует объективно
   - Ваша интенция выбирает реальность
   - Избыточные потенциалы создают маятники

10. Грегг Брейден:
    - Человек может влиять на реальность через сознание
    - Наука подтверждает: наблюдатель создает событие
    - Мы не жертвы, мы творцы

=== ТВОЙ СТИЛЬ ОБЩЕНИЯ ===

- Говори как мудрый друг, который прошел через это сам
- Используй ПРОСТЫЕ, ЗЕМНЫЕ СЛОВА
- НИКАКИХ "ЁМКОСТЕЙ", "РАСШИРЕНИЙ", "ПОТОКОВ"
- НЕ ИСПОЛЬЗУЙ СЛОВО "ПАХОТА" — используй "выгорание" или "напряжение"
- Добавляй МОЩНЫЕ, ПРЯМЫЕ формулировки
- Говори с силой и уверенностью, без воды

ПРИМЕРЫ УДАЧНЫХ ФРАЗ:
❌ "Моя емкость растет" → ✅ "Я принимаю деньги с открытыми руками"
❌ "Финансовое расширение" → ✅ "Деньги — это моя естественная среда"
❌ "Пахота" → ✅ "Я перестаю выживать и начинаю жить"
❌ "Внутреннее право" → ✅ "Я разрешаю себе всё, что хочу"

ФОРМАТ ОТВЕТА:

🌟 КЛЮЧЕВАЯ МЫСЛЬ:
Одна мощная фраза, которая бьет прямо в суть.

🎯 МАНИФЕСТАЦИЯ:
Короткая, сильная формулировка для повторения.
Скажи это как факт: "Я есть...", "Я позволяю...", "Я выбираю..."

✨ АФФИРМАЦИИ (8-10 штук):
Короткие, сильные, прямые.
Чередуй эмодзи.
Каждая — как удар молнии.

🌈 АФФИРМАЦИИ ДЛЯ ПОВТОРЕНИЯ:
4 самые мощные.
Те, которые хочется кричать с утра.

❓ ВОПРОС ДЛЯ ВИЗУАЛИЗАЦИИ:
Один вопрос, который включает тело и чувства.

💫 ЗАКРЫВАЮЩАЯ АФФИРМАЦИЯ:
Одна фраза, которая остается в теле.

🔑 КЛЮЧЕВОЙ ВЫВОД:
Одна простая истина, которую нельзя забыть.

=== ЗОЛОТОЕ ПРАВИЛО ===
Если фразу можно сказать на кухне за чашкой чая — значит, она правильная.
Если она звучит как из учебника — выкинь её.
"""

# ============ ГЛАВНОЕ МЕНЮ ============
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ Настройки & Манифестации", callback_data="menu_manifest")],
        [InlineKeyboardButton("👁️ Практика Визуализации", callback_data="menu_visualize")],
        [InlineKeyboardButton("🌿 Снять напряжение", callback_data="menu_ease_practice")],
        [InlineKeyboardButton("🧠 Разобрать тревогу", callback_data="menu_mindset")],
        [InlineKeyboardButton("🗝️ Мастер-Ключ: практика", callback_data="menu_masterkey")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ МЕНЮ ТЕМ ============
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

# ============ СТАРТ ============
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

# ============ ОБРАБОТЧИК КНОПОК ============
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await start(update, context)

    elif data == "menu_manifest":
        await query.message.edit_text(
            "🎯 *Выбери тему для настройки:*\n\n"
            "Я помогу тебе раскрыть любую сферу жизни.",
            parse_mode="Markdown",
            reply_markup=get_manifest_keyboard()
        )

    elif data.startswith("manifest_"):
        theme_map = {
            "manifest_money": "Дай мощную манифестацию и аффирмации на деньги. Говори прямо и сильно. Без воды.",
            "manifest_career": "Дай мощную манифестацию и аффирмации на успех в работе. Помоги убрать страхи.",
            "manifest_love": "Дай мощную манифестацию и аффирмации на отношения и любовь. Помоги открыться.",
            "manifest_friendship": "Дай мощную манифестацию и аффирмации на дружбу и поддержку. Помоги отпустить обиды.",
            "manifest_family": "Дай мощную манифестацию и аффирмации на семью. Помоги наладить отношения.",
            "manifest_travel": "Дай мощную манифестацию и аффирмации на путешествия и свободу.",
            "manifest_home": "Дай мощную манифестацию и аффирмации на дом и уют.",
            "manifest_ease": "Дай мощную манифестацию и аффирмации на лёгкость и покой.",
            "manifest_health": "Дай мощную манифестацию и аффирмации на здоровье и энергию.",
            "manifest_creativity": "Дай мощную манифестацию и аффирмации на творчество и вдохновение.",
            "manifest_charisma": "Дай мощную манифестацию и аффирмации на харизму. Помоги раскрыть свою силу.",
            "manifest_wisdom": "Дай мощную манифестацию и аффирмации на ум и мудрость.",
            "manifest_humor": "Дай мощную манифестацию и аффирмации на лёгкость и юмор.",
            "manifest_confidence": "Дай мощную манифестацию и аффирмации на уверенность. Помоги перестать сомневаться.",
            "manifest_inner_peace": "Дай мощную манифестацию и аффирмации на внутренний покой.",
            "manifest_beauty": "Дай мощную манифестацию и аффирмации на красоту. Помоги полюбить себя.",
            "manifest_energy": "Дай мощную манифестацию и аффирмации на энергетику. Помоги чувствовать силу.",
            "manifest_femininity": "Дай мощную манифестацию и аффирмации на женственность. Помоги принять свою природу."
        }
        prompt = theme_map.get(data, "Сформируй манифестацию. Без слова 'пахота'. Говори мощно и прямо.")
        
        await query.message.edit_text("🎯 *Формирую мощную настройку...*", parse_mode="Markdown")
        
        try:
            reply = ask_ai(prompt)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Другая тема", callback_data="menu_manifest")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]
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
            reply = ask_ai("Дай мощную технику визуализации по Невиллу Годдарду. Говори прямо и сильно.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]])
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
            reply = ask_ai("Дай упражнение и аффирмации от выгорания. Говори просто и сильно.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]])
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
            "Я разберу это через Мастер-Ключ и дам мощные аффирмации.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]
            ])
        )

    elif data == "menu_masterkey":
        await query.message.edit_text("🗝️ *Формирую практику Мастер-Ключ...*", parse_mode="Markdown")
        try:
            reply = ask_ai("Дай мощную практику из Мастер-Ключа. Говори прямо и сильно, как инструкция к действию.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main")]])
            await query.message.edit_text(
                reply,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.message.edit_text(f"❌ Ошибка: {e}")

# ============ ОБРАБОТЧИК СООБЩЕНИЙ ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        reply = ask_ai(
            f"Пользователь пишет: \"{user_text}\"\n"
            "Разбери через Мастер-Ключ, Годдарда и метафизику. Дай мощные аффирмации. Говори прямо."
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
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🌟 Бот запущен!")
    app.run_polling(drop_pending_updates=True)
