# Use a imagem base Python
FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo do diretório atual para o diretório de trabalho
COPY . .

# Expõe as portas necessárias
EXPOSE 5082

RUN python manage.py migrate --no-input

CMD ['python', 'manage.py', 'runserver', '0.0.0.0:5082']
