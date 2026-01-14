from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse, HttpRequest
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import transaction
import logging

from .models import (
    Topik,
    NewsPaper,
    ArticleInvite,
)
from .forms import (
    TopikForm,
    NewsPaperForm,
)

logger = logging.getLogger(__name__)


User = get_user_model()


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["counts"] = {
            "publishers": User.objects.count(),
            "topics": Topik.objects.count(),
            "newspapers": NewsPaper.objects.count(),
        }
        context["latest_newspapers"] = NewsPaper.objects.order_by("-published_date")[:5]
        return context


class TopikListView(ListView):
    """List all topics."""
    model = Topik
    template_name = "core/topic_list.html"
    context_object_name = "topics"


class TopikCreateView(CreateView):
    """Create a new topic."""
    model = Topik
    form_class = TopikForm
    template_name = "core/topic_form.html"
    success_url = reverse_lazy("core:topics_list")


class TopikUpdateView(UpdateView):
    """Update an existing topic."""
    model = Topik
    form_class = TopikForm
    template_name = "core/topic_form.html"
    success_url = reverse_lazy("core:topics_list")


class NewsPaperListView(ListView):
    """List all newspapers."""
    model = NewsPaper
    template_name = "core/newspaper_list.html"
    context_object_name = "newspapers"


class NewsPaperCreateView(LoginRequiredMixin, CreateView):
    """Create a newspaper and add the creator as a publisher."""
    model = NewsPaper
    form_class = NewsPaperForm
    template_name = "core/newspaper_form.html"
    success_url = reverse_lazy("core:newspapers_list")

    def form_valid(self, form: NewsPaperForm) -> render:
        response = super().form_valid(form)
        self.object.publishers.add(self.request.user)
        return response


class NewsPaperDetailView(DetailView):
    """Show a newspaper, its publishers and pending invites."""
    model = NewsPaper
    template_name = "core/newspaper_detail.html"
    context_object_name = "newspaper"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        newspaper = self.get_object()
        user = self.request.user
        is_auth_editor = (
            user.is_authenticated and (
                newspaper.publishers.filter(pk=user.pk).exists()
                or user.is_superuser
            )
        )
        context["can_invite"] = context["can_delete"] = is_auth_editor
        context["can_edit"] = is_auth_editor

        pending = newspaper.article_invites.filter(used=False)

        pending_info = []
        for inv in pending:
            invite_url = self.request.build_absolute_uri(
                reverse("core:accept_newspaper_invite", args=[str(inv.token)])
            )
            pending_info.append({"invite": inv, "invite_url": invite_url})

        context["pending_invites_info"] = pending_info
        return context


class CreateNewspaperInviteView(View):
    """Create an invite for a newspaper.

    Support AJAX; non-AJAX requests redirect back to the newspaper detail
    page and use Django messages to surface errors.
    """

    def post(self, request: HttpRequest, pk: int):
        newspaper = get_object_or_404(NewsPaper, pk=pk)

        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        if (
            request.user not in newspaper.publishers.all()
            and not request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You are not allowed to invite publishers to this newspaper."
            )

        email = request.POST.get("email", "").strip()
        logger.info(
            "create_newspaper_invite POST for newspaper %s email=%s AJAX=%s user=%s",
            newspaper.pk,
            email,
            request.headers.get("x-requested-with"),
            request.user,
        )
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if email.lower() == request.user.email:
            error = "You can't send and invite to yourself."
            if is_ajax:
                return JsonResponse({"success": False, "error": error}, status=400)
            messages.error(request, error)
            return redirect(
                reverse("core:newspaper_detail", args=[newspaper.pk])
            )

        if email and not (User.objects.filter(email__iexact=email).exists()):
            error = "No registered publisher with that email."
            if is_ajax:
                return JsonResponse({"success": False, "error": error}, status=400)
            messages.error(request, error)
            return redirect(newspaper.get_absolute_url())

        with transaction.atomic():
            n_locked = NewsPaper.objects.select_for_update().get(pk=newspaper.pk)

            if email:
                if ArticleInvite.objects.filter(
                    newspaper=n_locked, email__iexact=email, used=False
                ).exists():
                    error = "A pending invite for this email already exists."
                    if is_ajax:
                        return JsonResponse(
                            {"success": False, "error": error}, status=400
                        )
                    messages.error(request, error)
                    return redirect(newspaper.get_absolute_url())
            else:
                if ArticleInvite.objects.filter(newspaper=n_locked).filter(
                    (Q(email__isnull=True) | Q(email="")), used=False
                ).exists():
                    error = "A generic pending invite for this newspaper already exists."
                    if is_ajax:
                        return JsonResponse(
                            {"success": False, "error": error}, status=400
                        )
                    messages.error(request, error)
                    return redirect(newspaper.get_absolute_url())

            invite = ArticleInvite.objects.create(
                created_by=request.user,
                newspaper=newspaper,
                email=email,
            )
            invite_url = request.build_absolute_uri(
                reverse("core:accept_newspaper_invite", args=[str(invite.token)])
            )

            if email:
                logger.info(
                    "Invite created for email %s. Invite URL: %s",
                    email,
                    invite_url,
                )

        if is_ajax:
            pending = newspaper.article_invites.filter(used=False)
            pending_info = []
            for inv in pending:
                invite_url = request.build_absolute_uri(
                    reverse("core:accept_newspaper_invite", args=[str(inv.token)])
                )
                pending_info.append({"invite": inv, "invite_url": invite_url})
            pending_html = render_to_string(
                "invites/_pending_invites.html",
                {"pending_invites_info": pending_info},
                request=request,
            )
            return JsonResponse(
                {
                    "success": True,
                    "pending_html": pending_html,
                    "invite_url": invite_url,
                }
            )

        return render(
            request,
            "invites/newspaper_invite_sent.html",
            {
                "invite_url": invite_url,
                "email": email,
                "newspaper": newspaper,
                "invite": invite,
            },
        )

    def get(self, request: HttpRequest, pk: int):
        messages.info(
            request,
            "Use the inline modal on the newspaper page to create invites.",
        )
        newspaper = get_object_or_404(NewsPaper, pk=pk)
        return redirect(newspaper.get_absolute_url())


class AcceptNewspaperInviteView(View):
    def get(self, request: HttpRequest, token: str):
        invite = get_object_or_404(ArticleInvite, token=token, used=False)
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        if invite.email and invite.email.lower() != request.user.email.lower():
            return HttpResponseForbidden("This invite is not for your account.")

        invite.newspaper.publishers.add(request.user)
        invite.used = True
        invite.save()
        return render(
            request,
            "invites/newspaper_invite_accepted.html",
            {"newspaper": invite.newspaper, "user": request.user},
        )


class NewsPaperUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a newspaper (editor or superuser only)."""
    model = NewsPaper
    form_class = NewsPaperForm
    template_name = "core/newspaper_form.html"
    success_url = reverse_lazy("core:newspapers_list")

    def test_func(self) -> bool:
        newspaper = self.get_object()
        return (
            self.request.user in newspaper.publishers.all()
            or self.request.user.is_superuser
        )


class NewsPaperDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a newspaper (editor or superuser only)."""
    model = NewsPaper
    template_name = "core/newspaper_confirm_delete.html"
    success_url = reverse_lazy("core:newspapers_list")

    def test_func(self) -> bool:
        newspaper = self.get_object()
        return (
            self.request.user in newspaper.publishers.all()
            or self.request.user.is_superuser
        )


class SearchPublishersView(ListView):
    template_name = "core/partials/_publisher_list.html"
    context_object_name = "publishers"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            return User.objects.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            ).distinct()
        return User.objects.all()


class SearchTopicsView(ListView):
    template_name = "core/partials/_topic_list.html"
    context_object_name = "topics"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            return Topik.objects.filter(name__icontains=query).distinct()
        return Topik.objects.all()


class SearchNewspapersView(ListView):
    template_name = "core/partials/_newspaper_list.html"
    context_object_name = "newspapers"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            return NewsPaper.objects.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(topic__name__icontains=query)
            ).distinct()
        return NewsPaper.objects.all()
