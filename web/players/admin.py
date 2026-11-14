from django.contrib import admin
from .models import GameParticipant, GameRoom, PlayerProfile

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_id", "games", "wins", "losses", "xp")
    search_fields = ("user__username", "telegram_username", "telegram_id")

class GameParticipantInline(admin.TabularInline):
    model = GameParticipant
    extra = 0

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "host", "status", "created_at")
    list_filter = ("status",)
    inlines = [GameParticipantInline]
