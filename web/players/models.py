from django.conf import settings
from django.db import models

class PlayerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mafia_profile")
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=150, blank=True)
    games = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)

    @property
    def level(self):
        return self.xp // 100 + 1

    def __str__(self):
        return self.user.username

class GameRoom(models.Model):
    STATUS_CHOICES = [("waiting", "Kutmoqda"), ("active", "Faol"), ("finished", "Tugagan")]
    title = models.CharField(max_length=100, default="Mafia xonasi")
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="waiting")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} #{self.pk}"

class GameParticipant(models.Model):
    ROLE_CHOICES = [("mafia", "Mafia"), ("doctor", "Doktor"), ("detective", "Komissar"), ("citizen", "Tinch aholi")]
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, blank=True)
    alive = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["room", "user"], name="unique_room_player")]
