from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import OTP, SavedSong
import random
from .spotify_api import get_featured_songs, spotify
from spotipy.exceptions import SpotifyException
from .spotify_api import get_featured_songs, spotify
from .spotify_api import spotify
import requests
from django.shortcuts import redirect
from django.conf import settings


def get_featured_songs():

    result = spotify.search(q="top hits", type="track", limit=10)

    songs = []

    for track in result["tracks"]["items"]:

        songs.append(
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "image": (
                    track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else ""
                ),
                "spotify_url": track["external_urls"]["spotify"],
                "preview_url": track.get("preview_url"),
            }
        )

    return songs


def signup_page(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            error = "All fields are required."
        elif User.objects.filter(username=username).exists():
            error = "This username is already taken."
        elif User.objects.filter(email=email).exists():
            error = "An account with this email already exists."
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            otp = str(random.randint(100000, 999999))

            OTP.objects.create(user=user, otp=otp)

            send_mail(
                "Spotify Clone OTP",
                f"Your OTP is {otp}",
                "ravitank267@gmail.com",
                [email],
                fail_silently=False,
            )

            request.session["email"] = email

            return redirect("otp")

    return render(request, "signup.html", {"error": error})


def otp_page(request):

    email = request.session.get("email")

    user = User.objects.get(email=email)

    db_otp = OTP.objects.filter(user=user).last()

    if request.method == "POST":

        user_otp = request.POST.get("otp")

        if db_otp.otp == user_otp:

            return redirect("login")

    return render(request, "otp.html")


def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:

            login(request, user)

            return redirect("/")

    return render(request, "login.html")


def home_page(request):

    songs = get_featured_songs()

    context = {"songs": songs}

    return render(request, "home.html", context)


def api_search(request):

    query = request.GET.get("q")

    if not query:
        return JsonResponse({"error": "Missing search query."}, status=400)

    try:
        result = spotify.search(q=query, type="track", limit=20)
    except SpotifyException as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    songs = []
    for track in result["tracks"]["items"]:
        songs.append(
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "image": track["album"]["images"][0]["url"],
                "spotify_url": track["external_urls"]["spotify"],
            }
        )

    return JsonResponse({"songs": songs})


def api_featured(request):

    try:
        result = spotify.featured_playlists(limit=10, country="US")
    except SpotifyException as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    playlists = []
    for item in result["playlists"]["items"]:
        playlists.append(
            {
                "name": item["name"],
                "image": item["images"][0]["url"],
                "spotify_url": item["external_urls"]["spotify"],
            }
        )

    return JsonResponse({"featured": playlists})


def logout_page(request):

    logout(request)

    return redirect("login")


@login_required(login_url="/login/")
def saved_songs(request):

    songs = SavedSong.objects.filter(user=request.user)

    return render(request, "saved_songs.html", {"songs": songs})


@login_required(login_url="/login/")
def add_song(request):

    if request.method == "POST":

        name = request.POST.get("name")
        artist = request.POST.get("artist")
        image = request.POST.get("image")
        spotify_url = request.POST.get("spotify_url")

        if name and artist and spotify_url:
            SavedSong.objects.get_or_create(
                user=request.user,
                spotify_url=spotify_url,
                defaults={
                    "name": name,
                    "artist": artist,
                    "image": image or "",
                },
            )

    return redirect("saved_songs")




def search_song(request):

    query = request.GET.get("q", "")

    songs = []

    if query:

        try:

            result = spotify.search(
                q=query,
                type="track",
                limit=10
            )

            for track in result["tracks"]["items"]:

                songs.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "image": track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else "",

                    "spotify_url": track["external_urls"]["spotify"],

                    "preview_url": track.get("preview_url")
                })

        except SpotifyException as e:

            print("Spotify Error:", e)

    return render(
        request,
        "search.html",
        {
            "songs": songs,
            "query": query
        }
    )



def spotify_login(request):

    scope = (
        "streaming "
        "user-read-email "
        "user-read-private "
        "user-modify-playback-state "
        "user-read-playback-state"
    )

    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        f"&scope={scope}"
    )

    return redirect(auth_url)


def spotify_callback(request):

    code = request.GET.get("code")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        },
    )

    token_info = response.json()

    request.session["spotify_token"] = token_info["access_token"]

    return redirect("player")


def player(request):

    token = request.session.get("spotify_token")

    return render(request, "player.html", {"token": token})
