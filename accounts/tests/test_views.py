from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AccountsViewsTests(TestCase):
    def test_register_page_loads(self):
        resp = self.client.get(reverse("accounts:register"))
        self.assertEqual(resp.status_code, 200)

    def test_register_post_creates_user_and_redirects(self):
        resp = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "strongpass123",
                "password2": "strongpass123",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_login_page_loads(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)

    def test_logout_post_logs_out_user(self):
        user_model = get_user_model()
        user_model.objects.create_user(username="someone", password="pass1234")
        self.client.login(username="someone", password="pass1234")
        resp = self.client.post(reverse("accounts:logout"))
        self.assertEqual(resp.status_code, 302)

    def test_publishers_list_shows_users(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="alice",
            email="a@example.com",
            password="pw1234",
        )
        user_model.objects.create_user(
            username="bob",
            email="b@example.com",
            password="pw1234",
        )
        resp = self.client.get(reverse("accounts:publishers_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "alice")
        self.assertContains(resp, "bob")
