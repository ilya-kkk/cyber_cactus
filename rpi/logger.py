import socket
import json
import csv
import time
from datetime import datetime

IP = "10.0.0.2"   # Замените на IP вашего Arduino
PORT = 5000
CSV_FILE = "sensor_log.csv"
INTERVAL_SECONDS = 60  # опрос каждую минуту

# Проверка наличия заголовка в CSV
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
                sock.sendall(b"GET\n")
                data = sock.recv(1024).decode().strip()
                print("📥 Получено:", data)

                parsed = json.loads(data)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                row = [
                    now,
                    parsed["temperature"],
                    parsed["humidity_air"],
                    parsed["humidity_soil"]
                ]

                with open(CSV_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)

                print(f"✅ Записано: {row}")

        except Exception as e:
            print(f"❌ Ошибка подключения или обработки: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    init_csv()
    print("🚀 Запуск логгера... (нажмите Ctrl+C для остановки)")
    log_data()
