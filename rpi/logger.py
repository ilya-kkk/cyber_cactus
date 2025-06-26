import socket
import json
import csv
import time
from datetime import datetime

IP = "10.0.0.2"          # IP Arduino
PORT = 5000              # Порт, на котором слушает Arduino
CSV_FILE = "logs/sensor_log.csv"  # Обновленный путь к CSV файлу
INTERVAL_SECONDS = 60    # Интервал между опросами (в секундах)

# Инициализация CSV файла с заголовком
def init_csv():
    try:
        with open(CSV_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperature_C", "humidity_air_%", "humidity_soil_adc"])
    except FileExistsError:
        pass  # файл уже существует

# Основной цикл логгера
def log_data():
    while True:
        try:
            with socket.create_connection((IP, PORT), timeout=5) as sock:
                sock.sendall(b"GET\n")  # Отправляем сигнал на отправку данных

                # Получаем "поток" и читаем построчно
                file_like = sock.makefile()  # превращает сокет в файловый объект
                line = file_like.readline().strip()

                print("📥 Получено:", line)

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка разбора JSON: {e}")
                    continue

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                row = [
                    now,
                    data.get("temperature"),
                    data.get("humidity_air"),
                    data.get("humidity_soil")
                ]

                with open(CSV_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)

                print(f"✅ Записано в CSV: {row}")

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"❌ Ошибка подключения: {e}")
        except Exception as e:
            print(f"⚠️ Общая ошибка: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    print("🚀 Запуск логгера... (нажмите Ctrl+C для остановки)")
    init_csv()
    try:
        log_data()
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем.")
