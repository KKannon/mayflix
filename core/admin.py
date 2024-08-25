from django.contrib import admin
from core.models import Movie, Genre, Profile

models_list = [
    Movie,
    Genre,
    Profile
]

admin.site.register(models_list)