from django.contrib.auth.models import User
from django.db import models
import uuid

class Genre(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True, help_text="ID do gênero no TMDb")
    name = models.CharField(max_length=100, unique=True, help_text="Nome do gênero")

    def __str__(self):
        return self.name
    
class Movie(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=False)
    title = models.CharField(max_length=200, null=False, default='')
    imdb_id = models.CharField(max_length=200, null=False, default='', blank=True)
    tmdb_id = models.CharField(max_length=200, null=False, default='', blank=True, unique=True)
    sinopse = models.TextField(null=False, blank=True)
    duration = models.TimeField(blank=True, default='01:02:03')
    trailer_url = models.URLField(null=True, blank=True, default="")
    image_url = models.URLField(null=False)
    thumb_url = models.URLField(null=False)
    release_date = models.DateTimeField(null=False, blank=True)
    votes = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    genres = models.ManyToManyField(Genre, related_name="%(class)ss")
    adult = models.BooleanField(default=False)
    series = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def get_release_year(self):
        release = self.release_date.strftime("%Y")
        return f"{release}"

    def get_formatted_duration(self):
        total_seconds = self.duration.hour * 3600 + self.duration.minute * 60 + self.duration.second
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"

    def __str__(self) -> str:
        release = self.release_date.strftime("%d/%m/%Y")
        return f"{self.name} ({release})"
    
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    tag = models.CharField(max_length=200, blank=True)
    profile = models.URLField(null=True, blank=True)
    is_kid = models.BooleanField(default=False)
    favorites = models.ManyToManyField(Movie, related_name="%(class)ss")

    def __str__(self):
        return f"{self.name} -> {self.user.username}"