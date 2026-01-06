from django.test import TestCase
from django.urls import reverse

from .models import Publisher, NewsPaper, ArticleInvite


class ViewsTests(TestCase):
    def setUp(self) -> None:
        self.editor = Publisher.objects.create_user(
            username="editor",
            email="ed@example.com",
            password="pass1234",
        )
        self.other = Publisher.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass1234",
        )
        self.target = Publisher.objects.create_user(
            username="target",
            email="target@example.com",
            password="pass1234",
        )
        self.newspaper = NewsPaper.objects.create(
            title="Test paper",
            content="Body",
        )
        self.newspaper.publishers.add(self.editor)

    def test_edit_button_visible_to_editors(self) -> None:
        self.client.login(username="editor", password="pass1234")
        resp = self.client.get(
            reverse("core:newspaper_detail", args=[self.newspaper.pk])
        )
        self.assertContains(
            resp,
            reverse("core:newspaper_edit", args=[self.newspaper.pk]),
        )

    def test_edit_button_hidden_for_non_editors(self) -> None:
        self.client.login(username="other", password="pass1234")
        resp = self.client.get(
            reverse("core:newspaper_detail", args=[self.newspaper.pk])
        )
        self.assertNotContains(
            resp,
            reverse("core:newspaper_edit", args=[self.newspaper.pk]),
        )

    def test_create_invite_requires_authentication(self) -> None:
        resp = self.client.post(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk]),
            data={},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("core:login"), resp.url)

    def test_create_invite_requires_editor(self) -> None:
        self.client.login(username="other", password="pass1234")
        resp = self.client.post(
            reverse("core:newspaper_create_invite",
                    args=[self.newspaper.pk]),
            data={"email": self.target.email}
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_invite_for_registered_user(self) -> None:
        self.client.login(username="editor", password="pass1234")
        self.client.post(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk]),
            data={"email": self.target.email},
        )
        self.assertTrue(
            ArticleInvite.objects.filter(
                newspaper=self.newspaper,
                email__iexact=self.target.email,
                used=False,
            ).exists()
        )

    def test_duplicate_invite_rejected(self) -> None:
        self.client.login(username="editor", password="pass1234")
        ArticleInvite.objects.create(
            created_by=self.editor,
            newspaper=self.newspaper,
            email=self.target.email,
        )
        self.client.post(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk]),
            follow=True,
        )
        resp = self.client.post(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk]),
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertTrue(
            "A pending invite for this email already exists." in body
            or "A generic pending invite for this newspaper already exists." in body,
        )
        self.assertEqual(
            ArticleInvite.objects.filter(
                newspaper=self.newspaper,
                email__iexact=self.target.email,
                used=False,
            ).count(),
            1,
        )

    def test_get_create_invite_redirects_to_newspaper(self) -> None:
        resp = self.client.get(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(
            reverse("core:newspaper_detail", args=[self.newspaper.pk]),
            resp.url,
        )

    def test_ajax_create_invite(self) -> None:
        self.client.login(username="editor", password="pass1234")
        resp = self.client.post(
            reverse("core:newspaper_create_invite", args=[self.newspaper.pk]),
            data={"email": self.target.email},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIn("pending_html", data)

    def test_accept_invite(self) -> None:
        invite = ArticleInvite.objects.create(
            created_by=self.editor,
            newspaper=self.newspaper,
            email=self.target.email,
        )
        self.client.login(username="target", password="pass1234")
        resp = self.client.get(
            reverse("core:accept_newspaper_invite", args=[str(invite.token)])
        )
        self.assertEqual(resp.status_code, 200)
        invite.refresh_from_db()
        self.newspaper.refresh_from_db()
        self.assertTrue(invite.used)
        self.assertTrue(self.newspaper.publishers.filter(pk=self.target.pk).exists())

    def test_accept_invite_wrong_user_forbidden(self) -> None:
        invite = ArticleInvite.objects.create(
            created_by=self.editor,
            newspaper=self.newspaper,
            email=self.target.email,
        )
        self.client.login(username="other", password="pass1234")
        resp = self.client.get(
            reverse("core:accept_newspaper_invite", args=[str(invite.token)])
        )
        self.assertEqual(resp.status_code, 403)
        invite.refresh_from_db()
        self.assertFalse(invite.used)
