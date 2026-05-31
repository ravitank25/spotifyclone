from django.contrib import admin
from django.urls import path, include
from music import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_page, name="home"),
    path("signup/", views.signup_page, name="signup"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("otp/", views.otp_page, name="otp"),
    path("accounts/", include("allauth.urls")),
    path("search/", views.search_song, name="search_song"),
    path("api/search/", views.api_search, name="api_search"),
    path("api/featured/", views.api_featured, name="api_featured"),
    path("add-song/", views.add_song, name="add_song"),
    path("saved-songs/", views.saved_songs, name="saved_songs"),
    path("spotify-login/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="callback"),
    path("player/", views.player, name="player"),
]
