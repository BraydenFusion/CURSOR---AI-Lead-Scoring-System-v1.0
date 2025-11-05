# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
COPY start-railway.sh ./
COPY run_migrations.py ./
COPY ensure_users_table.py ./
RUN chmod +x start-railway.sh run_migrations.py ensure_users_table.py

EXPOSE 8000

CMD ["./start-railway.sh"]
