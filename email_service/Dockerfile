FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_BASE_URL=http://backend:8000
ENV SERVICE_HOST=0.0.0.0
ENV SERVICE_PORT=8002
ENV LOG_LEVEL=INFO

EXPOSE 8002

CMD ["python", "main.py"]
