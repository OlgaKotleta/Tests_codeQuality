FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/app/.venv/bin:$PATH"

COPY bot/ ./bot/

ENTRYPOINT ["/entrypoint.sh"]