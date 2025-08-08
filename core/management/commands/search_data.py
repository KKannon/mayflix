import time
import requests
from core.models import Movie
from django.core.management.base import BaseCommand
from core.utils import Utils
from django.conf import settings

class Command(BaseCommand):
    help = 'Busca dados de filmes e séries do TMDB e os processa.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--pages',
            type=int,
            default=10,
            help='Número de páginas a serem acessadas'
        )

        parser.add_argument(
            '-a', '--adult',
            type=bool,
            default=False,
            help='Filmes e Séries +18'
        )

    def handle(self, *args, **kwargs):
        TMDB_BASE_URL = settings.TMDB_BASE_URL
        TMDB_API_KEY = settings.TMDB_API_KEY
        LANGUAGE_CODE = settings.LANGUAGE_CODE
        num_pages = kwargs['pages']
        is_adult = kwargs['adult']


        if Movie.objects.count() > 0:
            self.stdout.write(self.style.SUCCESS('Base de filmes já foi pré-instalada!'))
            return

        all_movies_and_shows = []

        for i in range(num_pages):
            index_page = i + 1

            if is_adult:
                movies_18 = requests.get(f"{TMDB_BASE_URL}/search/movie?query=pornography&include_adult=true&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                m_18 = movies_18.json().get('results', [])
                for movie in m_18:
                    movie['is_serie'] = False

                series_18 = requests.get(f"{TMDB_BASE_URL}/search/tv?query=pornography&include_adult=true&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                s_18 = series_18.json().get('results', [])
                for show in s_18:
                    show['is_serie'] = True

                all_movies_and_shows.extend(m_18)
                all_movies_and_shows.extend(s_18)
            else:
                now_playing_movies_request = requests.get(f"{TMDB_BASE_URL}/movie/now_playing?include_adult=false&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                now_playing_movies = now_playing_movies_request.json().get('results', [])
                for movie in now_playing_movies:
                    movie['is_serie'] = False

                top_rated_shows_request = requests.get(f"{TMDB_BASE_URL}/tv/top_rated?include_adult=false&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                top_rated_shows = top_rated_shows_request.json().get('results', [])
                for show in top_rated_shows:
                    show['is_serie'] = True

                top_rated_request = requests.get(f"{TMDB_BASE_URL}/movie/top_rated?include_adult=false&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                top_rated_movies = top_rated_request.json().get('results', [])
                for movie in top_rated_movies:
                    movie['is_serie'] = False

                popular_tv_request = requests.get(f"{TMDB_BASE_URL}/tv/popular?include_adult=false&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                popular_tv_shows = popular_tv_request.json().get('results', [])
                for show in popular_tv_shows:
                    show['is_serie'] = True

                upcoming_request = requests.get(f"{TMDB_BASE_URL}/movie/upcoming?include_adult=false&api_key={TMDB_API_KEY}&language={LANGUAGE_CODE}&page={index_page}")
                upcoming_movies = upcoming_request.json().get('results', [])
                for show in upcoming_movies:
                    show['is_serie'] = True

                all_movies_and_shows.extend(now_playing_movies)
                all_movies_and_shows.extend(top_rated_movies)
                all_movies_and_shows.extend(top_rated_shows)
                all_movies_and_shows.extend(popular_tv_shows)
                all_movies_and_shows.extend(upcoming_movies)

            self.stdout.write(self.style.SUCCESS(f'Página: {index_page}, Quantidade de medias listadas: {len(all_movies_and_shows)}'))
            time.sleep(5)

        Utils.add_movies_query_selected(all_movies_and_shows, True)
        self.stdout.write(self.style.SUCCESS('Dados buscados e processados com sucesso.'))
