# Build from repo root: docker compose build bot

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot
COPY branding.json ./branding.json

ENV PYTHONPATH=/app
ENV BRANDING_PATH=/app/branding.json

CMD ["python", "bot/main.py"]
