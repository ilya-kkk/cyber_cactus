import logging
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os
import asyncio
import socket

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Путь к CSV
CSV_PATH = "logs/sensor_log.csv"
IP = "10.0.0.2"          # IP Arduino
PORT = 5000              # Порт, на котором слушает Arduino

# Функция отрисовки и возврата графиков
def generate_plots():
    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)

    metrics = {
        "temperature_C": "Температура (°C)",
        "humidity_air_%": "Влажность воздуха (%)",
        "humidity_soil_adc": "Влажность почвы (ADC)",
        "co2_adc": "CO₂ (ADC)"
    }

    # Создаем один график с четырьмя подграфиками
    fig, axes = plt.subplots(4, 1, figsize=(12, 12))
    fig.suptitle('Данные с датчиков', fontsize=16)

    for i, (column, label) in enumerate(metrics.items()):
        axes[i].plot(df.index, df[column], linestyle='-', linewidth=2)
        axes[i].set_title(label)
        axes[i].set_ylabel(label)
        axes[i].grid(True, alpha=0.3)
        
        # Поворачиваем метки времени для лучшей читаемости
        axes[i].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    
    # Сохраняем все графики в один файл
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf

# Функция отправки команды на Arduino
def send_relay_command(relay_num, state):
    try:
        with socket.create_connection((IP, PORT), timeout=5) as sock:
            command = f"{relay_num}{state}\n"
            sock.sendall(command.encode())
            response = sock.recv(1024).decode().strip()
            return response
    except Exception as e:
        logging.error(f"Ошибка отправки команды реле: {e}")
        return None

# Хэндлер команды /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📊 Данные с датчиков"],
        ["🔌 Реле 1 ВКЛ", "🔌 Реле 1 ВЫКЛ"],
        ["🔌 Реле 2 ВКЛ", "🔌 Реле 2 ВЫКЛ"],
        ["🔌 Реле 4 ВКЛ", "🔌 Реле 4 ВЫКЛ"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 Бот управления теплицей\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

# Хэндлер команды /stat
async def stat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        image = generate_plots()
        await update.message.reply_photo(photo=image)
        logging.info("✅ Графики отправлены пользователю.")
    except Exception as e:
        logging.error(f"Ошибка при обработке /stat: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при создании графиков.")

# Хэндлер текстовых сообщений (кнопки)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📊 Данные с датчиков":
        await stat_handler(update, context)
    
    elif text == "🔌 Реле 1 ВКЛ":
        response = send_relay_command(1, "ON")
        if response:
            await update.message.reply_text(f"✅ Реле 1 включено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка включения реле 1")
    
    elif text == "🔌 Реле 1 ВЫКЛ":
        response = send_relay_command(1, "OFF")
        if response:
            await update.message.reply_text(f"✅ Реле 1 выключено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка выключения реле 1")
    
    elif text == "🔌 Реле 2 ВКЛ":
        response = send_relay_command(2, "ON")
        if response:
            await update.message.reply_text(f"✅ Реле 2 включено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка включения реле 2")
    
    elif text == "🔌 Реле 2 ВЫКЛ":
        response = send_relay_command(2, "OFF")
        if response:
            await update.message.reply_text(f"✅ Реле 2 выключено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка выключения реле 2")
    
    elif text == "🔌 Реле 4 ВКЛ":
        response = send_relay_command(4, "ON")
        if response:
            await update.message.reply_text(f"✅ Реле 4 включено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка включения реле 4")
    
    elif text == "🔌 Реле 4 ВЫКЛ":
        response = send_relay_command(4, "OFF")
        if response:
            await update.message.reply_text(f"✅ Реле 4 выключено\nОтвет: {response}")
        else:
            await update.message.reply_text("❌ Ошибка выключения реле 4")

# Запуск бота
async def main():
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("stat", stat_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("🤖 Бот запущен. Ожидание команд...")
    
    # Инициализируем приложение перед запуском
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        # Держим бота запущенным
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если event loop уже запущен (например, в Jupyter или Docker), используем create_task
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        # Если нет текущего event loop, создаём новый
        asyncio.run(main())
