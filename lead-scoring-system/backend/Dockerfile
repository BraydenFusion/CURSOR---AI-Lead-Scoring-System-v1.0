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
COPY fix_migrations.py ./
COPY create_users_table_railway.py ./
COPY verify_and_fix_users_table.py ./
COPY create_leads_table_railway.py ./
COPY ensure_leads_table.py ./
COPY ensure_onboarding_fields.py ./
RUN chmod +x start-railway.sh run_migrations.py ensure_users_table.py fix_migrations.py create_users_table_railway.py verify_and_fix_users_table.py create_leads_table_railway.py ensure_leads_table.py ensure_onboarding_fields.py

EXPOSE 8000

CMD ["./start-railway.sh"]
