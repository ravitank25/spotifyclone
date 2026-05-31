from django.db import models
from django.contrib.auth.models import User

class OTP(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class SavedSong(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    image = models.URLField(max_length=500, blank=True)
    spotify_url = models.URLField(max_length=500)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "spotify_url")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.name} by {self.artist}"
