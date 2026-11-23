from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RegistrationPasswordValidationTests(TestCase):
    def test_common_password_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            {"username": "new-player", "password": "password123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="new-player").exists())

    def test_password_containing_username_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            {"username": "playername", "password": "playername12345"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="playername").exists())

    def test_valid_password_creates_account(self):
        response = self.client.post(
            reverse("register"),
            {"username": "new-player", "password": "G7!mQ2#vL9pR"},
        )

        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(get_user_model().objects.filter(username="new-player").exists())
