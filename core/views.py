# <====================================================================>
# Carregar credenciais do .env
# <====================================================================>
from mayflix.settings import TMDB_API_KEY, TMDB_BASE_URL, LANGUAGE_CODE

# <====================================================================>
# Carregar itens nativos do Django
# <====================================================================>
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpRequest
from django.urls import reverse

# <====================================================================>
# Carregar itens do código
# <====================================================================>
from core.models import Movie, Profile
from core.utils import Utils
from core.forms import ProfileForm

# <====================================================================>
# Api do imdb (opcional)
# <====================================================================>
from imdb import Cinemagoer

# <====================================================================>
# Requests para as APIS externas
# <====================================================================>
import requests

def Home(request:HttpRequest):
    """
        Carrega a página principal, sem nenhuma informação na parte superior da página.
    """
    return render(request, 'index.html', {"has_profile":False})

def Register(request:HttpRequest):
    """
        Página de registro dos usuários.
    """
    if request.method == 'POST':

        # <====================================================================>
        # Obter Informações do formulário enviado
        # <====================================================================>
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # <====================================================================>
        # Verificações básicas de registros
        # <====================================================================>
        if password1 != password2:
            messages.error(request, '⚠️ Senhas não coincidem! Tente Novamente')
            return redirect('Register')

        if User.objects.filter(username=username).exists():
            messages.error(request, '⚠️ Nome de usuário já existe!')
            return redirect('Register')

        if User.objects.filter(email=email).exists():
            messages.error(request, '⚠️ Email já utilizado!')
            return redirect('Register')
        
        # <====================================================================>
        # Criando e salvando a senha do usuário no banco de dados
        # <====================================================================>
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password1)
        user.save()

        # <====================================================================>
        # Criando os perfis primários! (Normal e Infantil)
        # <====================================================================>
        tag = str(username.replace(" ", "_")).lower()
        Profile.objects.create(user=user, tag="kids", name="Infantil", profile="", is_kid=True)
        Profile.objects.create(user=user, tag=tag, name=username, profile="https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg", is_kid=False)

        # <====================================================================>
        # Confirmar registro e redirecionar para login!
        # <====================================================================>
        messages.success(request, '✅ Registrado com sucesso!')
        return redirect('Login')

    return render(request, 'register.html',{"has_profile":False})

def Login(request:HttpRequest):
    """
        Página de login dos usuários.
    """
    if request.method == 'POST':
        # <====================================================================>
        # Obter Informações do formulário enviado
        # <====================================================================>
        username = request.POST['username']
        password = request.POST['password']


        # <====================================================================>
        # Verificações básicas de login
        # <====================================================================>
        user = authenticate(username=username, password=password)

        if not User.objects.filter(username=username).exists():
            messages.error(request, '⚠️ Usuário não existe!')
            return redirect('Login')

        if user is None:
            messages.error(request, '⚠️ Senha ou Nome de usuário incorreto!!')
            return redirect('Login')

        # <====================================================================>
        # Logar na conta e redirecionar para os perfis!
        # <====================================================================> 
        if user is not None:
            login(request, user)
            return redirect(reverse('Profile'))
        
    return render(request, 'login.html',{"has_profile":False})

@login_required(login_url='Login')
def Logout(request:HttpRequest):
    """
        Página de logout dos usuários.
    """
    logout(request)
    messages.success(request, '✅ Deslogado com sucesso!')
    return redirect(reverse('Login'))

@login_required(login_url='Login')
def Catalog(request:HttpRequest, profile_tag):
    """
        Página de catalogos dos usuários.
    """

    # <====================================================================>
    # Pegar informação do usuário e do perfil escolhido, para carregar os conteúdos
    # Se o perfil for infantil, carrega apenas filmes com genero 'Família'.
    # <====================================================================>
    user = request.user
    result = Utils.get_profile_and_genres(profile_tag, user)

    if not isinstance(result, tuple):
        return result

    pf, genres = result

    medias = Movie.objects.filter(genres__in=genres).order_by('?')[:300]
    media = medias.first()
    media.trailer_url = Utils.get_url_trailer(media)
    media.save()

    topics = Utils.organize(medias=medias)
    
    return render(request, 'catalog.html', {"media":media, "topics":topics, "profile":pf, "has_profile":True})

@login_required(login_url='Login')
def MovieDetails(request:HttpRequest, profile_tag, movie_id):
    if not request.user.is_authenticated:
        return redirect('Login')

    user = request.user
    result = Utils.get_profile_and_genres(profile_tag, user)

    if not isinstance(result, tuple):
        return result

    pf, genres = result
    media = Movie.objects.get(uuid=movie_id)
    media.trailer_url = Utils.get_url_trailer(media)
    media.save()

    # <====================================================================>
    # Verifica se o filme tem um id do IMDB para acessar o filme nas embed (opcional)
    # Se tiver alguma api que não use o imdb, pode usar apenas o tmdb.
    # <====================================================================>
    media = Utils.get_imdb_id(media)

    # <====================================================================>
    # Buscar outros filmes relacionados ao gênero do filme atual,
    # exceto o filme que está sendo visualizado (filtrado pelo ID).
    # <====================================================================>
    medias = Movie.objects.filter(genres__in=genres).exclude(pk=media.pk).distinct()[:8]
    
    # <====================================================================>
    # Organiza os filmes relacionados em tópicos, que serão exibidos na página.
    # <====================================================================>
    topics = [{
        "genre":"Relacionados",
        "medias": [{"uuid": str(movie.uuid), "title": movie.title, "release_date": movie.release_date, "image_url": movie.image_url} for movie in medias ]
        }]

    return render(request, 'catalog.html', {"media":media, "topics":topics, "profile":pf, "has_profile":True})

@login_required(login_url='Login')
def ListMedias(request:HttpRequest, profile_tag, query):
    if not request.user.is_authenticated:
        return redirect('Login')

    user = request.user
    result = Utils.get_profile_and_genres(profile_tag, user)

    if not isinstance(result, tuple):
        return result

    pf, genres = result
    
    organize_genre = False
    medias = []

    # <====================================================================>
    # Verificar a query de pesquisa. Dependendo do tipo da consulta (filmes, séries, favoritos),
    # diferentes tipos de conteúdo são carregados.
    # <====================================================================>
    match query:
        case "filmes":
            medias = Movie.objects.filter(genres__in=genres, series=False, tv=False)
            organize_genre = True

        case "series":
            medias = Movie.objects.filter(genres__in=genres, series=True, tv=True)
            organize_genre = True

        case "favoritos":
            medias = pf.favorites.all()
            topics = [
            {"genre": "Favoritos" if medias.count() > 0 else "Sua lista ainda está vazia!", "medias": 
                [{"uuid": str(movie.uuid), "title": movie.title, "release_date": movie.release_date, "image_url": movie.image_url} for movie in medias ]}
            ]

        case "mature":
            medias = Movie.objects.filter(genres__in=genres, adult=True)
            organize_genre = True

        case _:
            movie_info = str(query).replace(" ", "+").replace("%20", "+")

            found_movies = []
            found_series = []

            # <====================================================================>
            # Busca filmes na API externa (TMDB) usando a query de pesquisa.
            # <====================================================================>
            res = requests.get(f"{TMDB_BASE_URL}/search/movie?query={movie_info}&include_adult=true&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page=1")
            found_movies.extend(res.json().get('results', []))

            for movie in found_movies:
                movie['is_serie'] = False

            # <====================================================================>
            # Busca filmes na API externa (TMDB) usando a query de pesquisa.
            # <====================================================================>
            res = requests.get(f"{TMDB_BASE_URL}/search/tv?query={movie_info}&include_adult=true&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page=1")
            found_series.extend(res.json().get('results', []))

            for series in found_series:
                series['is_serie'] = True

            found_items = found_movies + found_series
            Utils.add_movies_query_selected(found_items)

            # <====================================================================>
            # Busca filmes locais cujo título contém a query de pesquisa.
            # <====================================================================>
            medias = Movie.objects.filter(title__icontains=str(query))

            # <====================================================================>
            # Organiza os resultados da pesquisa em tópicos para exibição.
            # <====================================================================>
            topics = [
                {"genre": str(query).title(), "medias": 
                    [{"uuid": str(movie.uuid), "title": movie.title, "release_date": movie.release_date, "image_url": movie.image_url} for movie in medias]}
                ]

    if organize_genre:
        topics = Utils.organize(medias=medias)

    return render(request, 'search.html', {"profile":pf, "topics":topics, "has_profile":True}) 

@login_required(login_url='Login')
def Profiles(request:HttpRequest):
    if not request.user.is_authenticated:
        return redirect('Login')
    
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.tag = profile.name.replace(" ", "_")
            profile.save()
            return redirect('Profile') 
    else:
        form = ProfileForm()

    # <====================================================================>
    # Carregar todos os perfis associados ao usuário logado.
    # <====================================================================>
    profiles = Profile.objects.filter(user=user)
    
    can_add_pfs = False if profiles.count() > 3 else True

    return render(request, 'profiles.html', {"profiles":profiles, "form":form, "has_profile":False, "can_add_pfs":can_add_pfs}) 

@login_required(login_url='Login')
def DelProfile(request:HttpRequest, profile_id):
    if not request.user.is_authenticated:
        return redirect('Login')
    
    user = request.user

    profile = Profile.objects.get(user=user, pk=profile_id)

    profile.delete()
            
    return redirect('Profile')

@login_required(login_url='Login')
def Watch(request, profile_tag, movie_id):
    if not request.user.is_authenticated:
        return redirect('Login')

    user = request.user
    result = Utils.get_profile_and_genres(profile_tag, user)

    if not isinstance(result, tuple):
        return result

    pf, genres = result

    # <====================================================================>
    # Carrega os detalhes do filme que será assistido.
    # <====================================================================>
    media = Movie.objects.get(uuid=movie_id)

    # <====================================================================>
    # Verifica se o filme tem um id do IMDB para acessar o filme nas embed (opcional)
    # Se tiver alguma api que não use o imdb, pode usar apenas o tmdb.
    # <====================================================================>
    media = Utils.get_imdb_id(media)
    embed = Utils.get_embed(media.imdb_id, media.series)

    print(embed)

    return render(request, 'watch.html', {"media":media, "embed":embed, "profile":pf, "has_profile":True})