FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y curl
RUN uv sync

ENV SERVICE_NAME=""

CMD ["sh", "-c", "uv run --package $SERVICE_NAME --with fastapi -- fastapi run services/$SERVICE_NAME/app/main.py --host 0.0.0.0 --port 8000"]
