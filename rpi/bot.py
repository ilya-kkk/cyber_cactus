import logging
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Путь к CSV
CSV_PATH = "logs/sensor_log.csv"

# Функция отрисовки и возврата графиков
def generate_plots():
    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)

    metrics = {
        "temperature_C": "Температура (°C)",
        "humidity_air_%": "Влажность воздуха (%)",
        "humidity_soil_adc": "Влажность почвы (ADC)"
    }

    images = []

    for column, label in metrics.items():
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[column], marker='o', linestyle='-')
        plt.title(label)
        plt.xlabel("Время")
        plt.ylabel(label)
        plt.grid(True)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        images.append(buf)

        plt.close()

    return images

# Хэндлер команды /stat
async def stat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        images = generate_plots()

        for img in images:
            await update.message.reply_photo(photo=img)

        logging.info("✅ Графики отправлены пользователю.")
    except Exception as e:
        logging.error(f"Ошибка при обработке /stat: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при создании графиков.")

# Запуск бота
async def main():
      
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("stat", stat_handler))

    print("🤖 Бот запущен. Ожидание команд...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
