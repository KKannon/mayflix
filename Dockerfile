# Use a imagem base Python
FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5082

RUN python manage.py search_data

RUN python manage.py migrate --no-input

CMD ['python', 'manage.py', 'runserver', '0.0.0.0:5082']
