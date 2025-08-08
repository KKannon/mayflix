# Use a imagem base Python
FROM python:3.11-slim

# Evita buffering nos logs
ENV PYTHONUNBUFFERED=1

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (para psycopg2, Pillow etc., se necessário)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Coleta arquivos estáticos
RUN python manage.py collectstatic --no-input

# Expõe a porta (ajuste conforme necessário)
EXPOSE 5082

# Comando padrão: Gunicorn (não usar runserver)
CMD ["gunicorn", "nome_do_projeto.wsgi:application", "--bind", "0.0.0.0:5082", "--workers", "3"]
