from core.models import Movie, Genre, Profile
from django.shortcuts import redirect
from mayflix.settings import TMDB_API_KEY
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.utils import timezone
from imdb import Cinemagoer
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
import requests

class Utils:

    @staticmethod
    def get_profile_and_genres(profile_tag, user):
        """Obtém o perfil do usuário com base no 'profile_tag' e no usuário autenticado.
        Se o perfil não existir, redireciona para a página de seleção de perfis.
        Verifica se o perfil é infantil; se sim, filtra apenas o gênero 'Família'.""" 
       
        try:
            pf = Profile.objects.get(tag__icontains=profile_tag, user=user)
        except Profile.DoesNotExist:
            return redirect('Profile')

        if not pf:
            return redirect('Login')

        if pf.is_kid:
            genres = Genre.objects.filter(tmdb_id=10751)
        else:
            genres = Genre.objects.all()

        return pf, genres

    @staticmethod
    def organize(medias):
        """
            Separador de conteúdo por gênero: 
            # Exemplo
            return [
                {
                    'genre': 'terror', 'medias': ['Chucky', 'O Exorcismo']
                }
            ]
        """
        genre_dict = {}
        used_movies = set()

        # <====================================================================>
        # Itera sobre os filmes/séries para organizá-los em um dicionário baseado no gênero.
        # O objetivo é agrupar as mídias por gênero e limitar o número de mídias a 8 por gênero.
        # <====================================================================>
        for movie in medias:
            movie_genres = movie.genres.all()
            for genre in movie_genres:
                genre_name = genre.name
                if genre_name not in genre_dict:
                    genre_dict[genre_name] = []

                if movie not in used_movies and len(genre_dict[genre_name]) < 8:
                    genre_dict[genre_name].append(movie)
                    used_movies.add(movie)

        # <====================================================================>
        # Limita o número de gêneros exibidos para 10.
        # <====================================================================>
        limited_genre_dict = dict(list(genre_dict.items())[:10])


        # <====================================================================>
        # Constrói a lista de tópicos a serem exibidos, cada um contendo um gênero e suas mídias.
        # <====================================================================>
        topics = [
            {"genre": genre, "medias": 
            [{"uuid": str(movie.uuid), "title": movie.title, "release_date": movie.release_date, "image_url": movie.image_url} for movie in medias]}
            for genre, medias in limited_genre_dict.items()
        ]

        last_topics = []

        # <====================================================================>
        # Filtra os tópicos para garantir que apenas gêneros com mídias sejam retornados.
        # <====================================================================>
        for topic in topics:
            if len(topic['medias']) > 0:
                last_topics.append(topic)

        return last_topics


    @staticmethod
    def add_movies_query_selected(results, debug=False):
        """
            Adicionar filmes depois de uma pesquisa no tmbd_api.
            Passando apenas os 'results' da request
        """
        TMDB_BASE_URL = 'https://api.themoviedb.org/3'
        LANGUAGE = 'pt-BR'

        # <====================================================================>
        # Itera sobre os resultados obtidos na API, adicionando-os ao banco de dados caso não existam.
        # Para cada resultado, associa os gêneros correspondentes, e adiciona as informações principais do filme/série.
        # <====================================================================>
        for item in results:
            genre_objects = []
            if 'genre_ids' in item:
                for genre_id in item['genre_ids']:
                    try:
                        # <====================================================================>
                        # Busca ou cria os gêneros associados ao filme/série com base nos IDs dos gêneros.
                        # <====================================================================>
                        genre_obj, created = Genre.objects.get_or_create(tmdb_id=genre_id, defaults={'name': 'Unknown'})
                        genre_objects.append(genre_obj)
                    except IntegrityError:
                        continue

            is_serie = item.get('is_serie', False)
            is_movie = not is_serie

            try:
                # <====================================================================>
                # Converte a data de lançamento da string para um objeto datetime.
                # <====================================================================>
                release_date_str = item.get('release_date') or item.get('first_air_date', '1970-01-01')
                release_date = timezone.make_aware(datetime.strptime(release_date_str, '%Y-%m-%d'), timezone.get_current_timezone())

                # <====================================================================>
                # Busca ou cria o filme/série no banco de dados, e associa as informações adicionais.
                # <====================================================================>
                movie_obj, created = Movie.objects.get_or_create(
                    tmdb_id=item['id'],
                    defaults={
                        'name': item.get('original_title') or item.get('original_name'),
                        'title': item.get('title') or item.get('name'),
                        'sinopse': item.get('overview', ''),
                        'release_date': release_date,
                        'image_url': f"https://image.tmdb.org/t/p/original{item.get('poster_path', '')}",
                        'thumb_url': f"https://image.tmdb.org/t/p/w500{item.get('backdrop_path', '')}",
                        'votes': item.get('vote_average', 0),
                        'duration': '01:02:03',
                        'adult': item.get('adult', False),
                        'series': is_serie,
                        'tv': is_serie,
                    }
                )
                
                # <====================================================================>
                # Se o filme/série foi criado, associa os gêneros e salva no banco de dados.
                # Caso contrário, apenas exibe uma mensagem de depuração se estiver no modo debug.
                # <====================================================================>
                if created:
                    movie_obj.genres.set(genre_objects)
                    movie_obj.save()
                    if debug:
                        print(f"Added {'movie' if is_movie else 'show'}: {movie_obj.title} with genres {', '.join([g.name for g in genre_objects])}","\n")
                else:
                    if debug:
                        print(f"{'Movie' if is_movie else 'Show'} {movie_obj.title} already exists in the database.","\n")
            except Exception as e:
                # <====================================================================>
                # Captura exceções durante o processo de adição e continua a execução.
                # <====================================================================>
                print(e)
                pass