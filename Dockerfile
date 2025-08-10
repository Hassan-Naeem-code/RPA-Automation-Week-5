# Dockerfile for Inventory Bot
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/ ./bot/
CMD ["python", "bot/inventory_bot.py"]
