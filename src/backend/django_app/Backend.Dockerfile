FROM python:3.12.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=true

RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY src/backend/django_app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/imgs
RUN mkdir -p /app/db
RUN chmod 755 /app/imgs /app/db

ENV WKHTMLTOIMAGE_PATH=/usr/bin/wkhtmltoimage

EXPOSE 8000

CMD ["sh", "-c", "cd /app/src/backend/django_app && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]