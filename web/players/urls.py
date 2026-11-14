from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("rooms/", views.rooms, name="rooms"),
    path("rooms/create/", views.create_room, name="create_room"),
    path("rooms/<int:room_id>/join/", views.join_room, name="join_room"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("api/telegram-sync/", views.telegram_sync, name="telegram_sync"),
]
