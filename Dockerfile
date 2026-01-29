FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN pip install --no-cache-dir telethon==1.34.0

# Копируем ВСЕ файлы из репозитория
COPY . .

# Создаем сессию если её нет (автоматически)
RUN if [ ! -f genesis_session.session ]; then \
    echo "⚠️ Session file not found, creating dummy..."; \
    touch genesis_session.session; \
    fi

# Запускаем бота
CMD ["python", "main.py"]
