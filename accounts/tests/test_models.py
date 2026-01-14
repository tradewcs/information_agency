from django.test import TestCase
from django.contrib.auth import get_user_model


class PublisherModelTests(TestCase):
    def test_str_returns_username(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="alice")
        self.assertEqual(str(user), "alice")
