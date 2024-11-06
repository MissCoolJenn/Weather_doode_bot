# Используем базовый образ Python
FROM python:3.10.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные утилиты и PostgreSQL клиент
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    # Добавление libpq-dev для компиляции PostgreSQL зависимостей
    libpq-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем Python-библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код в контейнер
COPY . .

# Запуск бота
CMD ["python", "Weather_bot.py"]