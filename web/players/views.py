import json
import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import GameParticipant, GameRoom, PlayerProfile

def ensure_profile(user):
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    return profile

def home(request):
    top = PlayerProfile.objects.select_related("user").order_by("-wins", "-xp")[:5]
    return render(request, "players/home.html", {"top": top})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or len(password) < 8:
            messages.error(request, "Login kiriting. Parol kamida 8 belgidan iborat bo‘lsin.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu login band.")
        else:
            candidate = User(username=username)
            try:
                validate_password(password, user=candidate)
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)
            else:
                user = User.objects.create_user(username=username, password=password)
                ensure_profile(user)
                login(request, user)
                return redirect("profile")
    return render(request, "players/register.html")

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            ensure_profile(user)
            return redirect("profile")
        messages.error(request, "Login yoki parol noto‘g‘ri.")
    return render(request, "players/login.html")

@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def profile(request):
    return render(request, "players/profile.html", {"profile": ensure_profile(request.user)})

def leaderboard(request):
    players = PlayerProfile.objects.select_related("user").order_by("-wins", "-xp", "user__username")
    return render(request, "players/leaderboard.html", {"players": players})

@login_required
def rooms(request):
    available = GameRoom.objects.filter(status="waiting").order_by("-created_at")
    return render(request, "players/rooms.html", {"rooms": available})

@login_required
@require_POST
def create_room(request):
    room = GameRoom.objects.create(host=request.user)
    GameParticipant.objects.create(room=room, user=request.user)
    return redirect("room_detail", room_id=room.id)

@login_required
@require_POST
def join_room(request, room_id):
    room = get_object_or_404(GameRoom, pk=room_id, status="waiting")
    if room.participants.count() >= 12:
        messages.error(request, "Xonada joy qolmagan.")
    else:
        GameParticipant.objects.get_or_create(room=room, user=request.user)
    return redirect("room_detail", room_id=room.id)

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(GameRoom.objects.prefetch_related("participants__user"), pk=room_id)
    # Active games are private to their participants; outsiders must not inspect the room.
    if room.status == "active" and not room.participants.filter(user=request.user).exists():
        return HttpResponseForbidden("Faol o‘yinga faqat ishtirokchilar kira oladi.")
    if request.method == "POST" and request.POST.get("action") == "start":
        if room.host_id != request.user.id or room.status != "waiting":
            return HttpResponseForbidden("Faqat xona egasi kutish xonasini boshlashi mumkin.")
        participants = list(room.participants.all())
        if len(participants) < 5:
            messages.error(request, "O‘yinni boshlash uchun kamida 5 o‘yinchi kerak.")
        else:
            ids = list(range(len(participants)))
            random.shuffle(ids)
            roles = ["mafia"] * max(1, len(participants) // 4) + ["doctor", "detective"]
            roles += ["citizen"] * (len(participants) - len(roles))
            random.shuffle(roles)
            with transaction.atomic():
                for participant, role in zip(participants, roles):
                    participant.role = role
                    participant.alive = True
                    participant.save(update_fields=["role", "alive"])
                room.status = "active"
                room.save(update_fields=["status"])
            messages.success(request, "O‘yin boshlandi! Har bir ishtirokchi o‘z rolini profil xonasida ko‘ra oladi.")
    return render(request, "players/room_detail.html", {"room": room, "my_participant": room.participants.filter(user=request.user).first()})

@csrf_exempt
@require_POST
def telegram_sync(request):
    if not settings.TELEGRAM_SYNC_KEY or request.headers.get("X-Telegram-Sync-Key") != settings.TELEGRAM_SYNC_KEY:
        return HttpResponseForbidden("Invalid sync key")
    try:
        data = json.loads(request.body or "{}")
        telegram_id = int(data["telegram_id"])
        username = str(data.get("username") or "")[:150]
        games = max(0, int(data.get("games", 0)))
        wins = max(0, int(data.get("wins", 0)))
        losses = max(0, int(data.get("losses", 0)))
        xp = max(0, int(data.get("xp", 0)))
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid payload"}, status=400)
    profile = PlayerProfile.objects.filter(telegram_id=telegram_id).first()
    if profile is None:
        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}", defaults={"is_active": False})
        profile = ensure_profile(user)
        profile.telegram_id = telegram_id
    profile.telegram_username = username
    profile.games, profile.wins, profile.losses, profile.xp = games, wins, losses, xp
    profile.save()
    return JsonResponse({"ok": True, "profile_id": profile.id})
