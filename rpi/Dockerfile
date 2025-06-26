FROM arm64v8/python:3.9-slim

WORKDIR /app

# Копируем файл логгера
COPY logger.py .

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем права на запись
RUN chmod +x logger.py

# Запускаем логгер
CMD ["python", "logger.py"] 