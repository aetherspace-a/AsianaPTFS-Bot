FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY branding.json /app/branding.json
COPY assets /app/assets
RUN mkdir -p /app/storage/boarding_passes

ENV PYTHONPATH=/app
ENV BRANDING_PATH=/app/branding.json
ENV ASSETS_PATH=/app/assets
ENV BOARDING_PASSES_PATH=/app/storage/boarding_passes

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
