FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-cache-dir

COPY foodgram/ .

RUN python3 manage.py collectstatic --noinput

CMD ["sh", "-c", "\
    while ! nc -z db 5432; do sleep 2; echo 'Waiting for PostgreSQL...'; done && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    (gunicorn --bind 0.0.0.0:8000 foodgram.wsgi:application & \
     daphne -b 0.0.0.0 -p 8001 foodgram.asgi:application)"]
