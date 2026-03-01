FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code into the backend/ package directory
COPY . ./backend/

# Cloud Run sets PORT env var (defaults to 8080)
ENV PORT=8080
EXPOSE 8080

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
