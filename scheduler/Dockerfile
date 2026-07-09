FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_BASE_URL=http://backend:8000
ENV SCHEDULER_INTERVAL_MINUTES=5
ENV NOTIFICATION_WINDOW_DAYS=3
ENV LOG_LEVEL=INFO

EXPOSE 8001

CMD ["python", "main.py", "run"]
