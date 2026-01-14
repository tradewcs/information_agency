from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from uuid import UUID

from core.models import Topik, NewsPaper, ArticleInvite


class TopikModelTests(TestCase):
    def test_str(self):
        topic = Topik.objects.create(name="Science")
        self.assertEqual(str(topic), "Science")


class NewsPaperModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="pass",
        )
        self.topic = Topik.objects.create(name="Tech")

    def test_str_and_get_absolute_url_and_relations(self):
        np = NewsPaper.objects.create(title="My News", content="Content")
        np.topic.add(self.topic)
        np.publishers.add(self.user)

        self.assertEqual(str(np), "My News")
        self.assertEqual(
            np.get_absolute_url(),
            reverse("core:newspaper_detail", args=[np.pk]),
        )
        self.assertIn(self.topic, np.topic.all())
        self.assertIn(self.user, np.publishers.all())


class ArticleInviteModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="bob",
            password="pass",
        )
        self.newspaper = NewsPaper.objects.create(title="Paper", content="C")

    def test_str_with_email_and_without(self):
        invite1 = ArticleInvite.objects.create(
            created_by=self.user,
            newspaper=self.newspaper,
            email="test@example.com",
        )
        self.assertIn("test@example.com", str(invite1))
        self.assertIn(self.user.username, str(invite1))

        invite2 = ArticleInvite.objects.create(
            created_by=self.user,
            newspaper=self.newspaper,
        )
        self.assertIn("any", str(invite2))

    def test_token_is_uuid(self):
        invite = ArticleInvite.objects.create(
            created_by=self.user,
            newspaper=self.newspaper,
        )
        self.assertIsInstance(invite.token, UUID)
