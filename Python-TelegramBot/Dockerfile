FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/Python-TelegramBot/
CMD ["python", "Python-TelegramBot/manage.py", "runserver", "0.0.0.0:8000"]