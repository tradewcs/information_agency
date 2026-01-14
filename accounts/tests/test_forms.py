from django.test import TestCase
from accounts.forms import RegistrationForm
from django.contrib.auth import get_user_model


class RegistrationFormTests(TestCase):
    def test_passwords_must_match(self):
        form = RegistrationForm(
            data={
                "username": "bob",
                "email": "bob@example.com",
                "password1": "pass1234",
                "password2": "different",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_save_sets_password_and_lowercases_email(self):
        form = RegistrationForm(
            data={
                "username": "carol",
                "email": "CAROL@EXAMPLE.COM",
                "password1": "secret123",
                "password2": "secret123",
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "carol@example.com")
        self.assertTrue(get_user_model().objects.filter(username="carol").exists())
        self.assertTrue(user.check_password("secret123"))
