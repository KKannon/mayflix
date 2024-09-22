from django import urls
from core import views
from django.urls import path

urlpatterns = [
    path('', views.Home, name='Home'),
    path('register', views.Register, name='Register'),
    path('login', views.Login, name='Login'),
    path('logout', views.Logout, name='Logout'),
    path('profile', views.Profiles, name='Profile'),
    path('delete-profile/<int:profile_id>', views.DelProfile, name='DelProfile'),
    path('catalog', views.Catalog, name='Recommendations'),
    path('list/<str:profile_tag>/<str:query>', views.ListMedias, name='ListMedias'),
    path('<str:profile_tag>/catalog', views.Catalog, name='Recommendations'),
    path('movie/<str:profile_tag>/<str:movie_id>', views.MovieDetails, name='MovieDetails'),
    path('watch/<str:profile_tag>/<str:movie_id>', views.Watch, name='Watch'),
]