# MayFlix 🎬

Bem-vindo ao MayFlix – uma aplicação de código aberto para gerenciamento de filmes e séries, desenvolvida em Python usando o framework Django. Este projeto tem como objetivo fornecer uma plataforma simples e eficiente para organizar e explorar uma coleção de conteúdos audiovisuais, funcionando como um catálogo personalizado.

## 🛠️ Tecnologias Utilizadas

- Python 3.x: Linguagem de programação utilizada no backend.
- Django: Framework web em Python, utilizado para a construção da aplicação.
- SQLite: Banco de dados padrão do Django, utilizado para armazenar informações sobre filmes e séries.

## 🚀 Funcionalidades
- Catálogo de Filmes e Séries: Visualize, adicione, edite e remova informações de filmes e séries.
- Classificação e Gêneros: Organize o conteúdo por gênero, classificação etária, e outros filtros.
- Pesquisa e Navegação: Ferramentas de pesquisa integradas para facilitar a navegação e a busca de títulos.
- Administração: Interface administrativa do Django para gerenciar conteúdos de forma eficiente

## 📦 Como Instalar

- Clone este repositório:
```sh
git clone https://github.com/seu-usuario/mayflix.git
cd mayflix
```
- Crie e ative um ambiente virtual:
```sh
python -m venv env
source venv/bin/activate # No Windows: env\Scripts\activate
```
- Instale as dependências do projeto:

```sh
pip install -r requirements.txt
```
- Realize as migrações do banco de dados:

```py
python manage.py migrate
```
- Inicie o servidor local:

- Acesse a aplicação no seu navegador através de http://127.0.0.1:8000/.
```py
python manage.py runserver
```

# 🚢 Como iniciar um servidor com docker?
- Primeiro precisa construir a imagem do sistema, Depois inicie a imagem:
 

```bash
docker build -t mayflix .

docker run -d -p 5082:5082 --restart=always --name mayflix-docker mayflix
```


# Licença
Este projeto é licenciado sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.
