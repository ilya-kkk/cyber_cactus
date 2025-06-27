import logging
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
import asyncio

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

    # Создаем один график с тремя подграфиками
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
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

# Хэндлер команды /stat
async def stat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        image = generate_plots()
        await update.message.reply_photo(photo=image)
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
