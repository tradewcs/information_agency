from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import transaction
import logging

from .models import (
    Publisher,
    Topik,
    NewsPaper,
    EmailVerificationToken,
    ArticleInvite,
)
from .forms import (
    PublisherForm,
    TopikForm,
    NewsPaperForm,
    RegistrationForm,
)

logger = logging.getLogger(__name__)


def index(request):
    """Simple homepage with counts and recent newspapers."""
    counts = {
        "publishers": Publisher.objects.count(),
        "topics": Topik.objects.count(),
        "newspapers": NewsPaper.objects.count(),
    }
    latest_newspapers = NewsPaper.objects.order_by("-published_date")[:5]
    return render(
        request,
        "index.html",
        {"counts": counts, "latest_newspapers": latest_newspapers},
    )


class PublisherListView(ListView):
    """List all publishers."""
    model = Publisher
    template_name = "core/publisher_list.html"
    context_object_name = "publishers"


class PublisherCreateView(CreateView):
    """Create a new publisher account."""
    model = Publisher
    form_class = PublisherForm
    template_name = "core/publisher_form.html"
    success_url = reverse_lazy("core:publishers_list")


class PublisherDetailView(DetailView):
    """Show details for a publisher."""
    model = Publisher
    template_name = "core/publisher_detail.html"
    context_object_name = "publisher"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["can_edit"] = (
            self.request.user == obj or self.request.user.is_superuser
        )
        return context


class PublisherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a publisher's profile (self or superuser)."""
    model = Publisher
    form_class = PublisherForm
    template_name = "core/publisher_form.html"
    success_url = reverse_lazy("core:publishers_list")

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj or self.request.user.is_superuser


def publisher_articles(request, pk):
    """Show a simple list of newspapers authored by a publisher."""
    publisher = get_object_or_404(Publisher, pk=pk)
    newspapers = NewsPaper.objects.filter(
        publishers=publisher
    ).order_by("-published_date")
    return render(
        request,
        "core/publisher_articles.html",
        {"publisher": publisher, "newspapers": newspapers},
    )


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

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.publishers.add(self.request.user)
        return response


class NewsPaperDetailView(DetailView):
    """Show a newspaper, its publishers and pending invites."""
    model = NewsPaper
    template_name = "core/newspaper_detail.html"
    context_object_name = "newspaper"

    def get_context_data(self, **kwargs):
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


def create_newspaper_invite(request, pk):
    """Create an invite for a newspaper.

    Support AJAX; non-AJAX requests redirect back to the newspaper detail
    page and use Django messages to surface errors.
    """
    newspaper = get_object_or_404(NewsPaper, pk=pk)

    if not request.user.is_authenticated:
        return redirect(f"{reverse('core:login')}?next={request.path}")

    if (
        request.user not in newspaper.publishers.all()
        and not request.user.is_superuser
    ):
        return HttpResponseForbidden(
            "You are not allowed to invite publishers to this newspaper."
        )

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        logger.info(
            "create_newspaper_invite POST for newspaper %s email=%s AJAX=%s "
            "user=%s",
            newspaper.pk,
            email,
            request.headers.get("x-requested-with"),
            request.user,
        )
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if email.lower() == request.user.email:
            error = "You can't send and invite to yourself."
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": error},
                    status=400,
                )
            messages.error(request, error)
            return redirect(
                reverse("core:newspaper_detail", args=[newspaper.pk])
            )

        if email and not (
            Publisher.objects.filter(email__iexact=email).exists()
        ):
            error = "No registered publisher with that email."
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": error},
                    status=400,
                )
            messages.error(request, error)
            return redirect(newspaper.get_absolute_url())

        with transaction.atomic():
            n_locked = NewsPaper.objects.select_for_update().get(
                pk=newspaper.pk
            )

            if email:
                if ArticleInvite.objects.filter(
                    newspaper=n_locked,
                    email__iexact=email,
                    used=False,
                ).exists():
                    error = "A pending invite for this email already exists."
                    if is_ajax:
                        return JsonResponse(
                            {"success": False, "error": error},
                            status=400,
                        )
                    messages.error(request, error)
                    return redirect(newspaper.get_absolute_url())
            else:
                if ArticleInvite.objects.filter(newspaper=n_locked).filter(
                    (Q(email__isnull=True) | Q(email="")),
                    used=False,
                ).exists():
                    error = "A generic pending invite for this newspaper already exists."
                    if is_ajax:
                        return JsonResponse(
                            {"success": False, "error": error},
                            status=400,
                        )
                    messages.error(request, error)
                    return redirect(newspaper.get_absolute_url())

            invite = ArticleInvite.objects.create(
                created_by=request.user,
                newspaper=newspaper,
                email=email,
            )
            invite_url = request.build_absolute_uri(
                reverse(
                    "core:accept_newspaper_invite",
                    args=[str(invite.token)],
                )
            )
            if email:
                send_mail(
                    subject=(
                        f"Invite to collaborate on '{newspaper.title}'"
                    ),
                    message=(
                        f"Accept invitation: {invite_url}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )

        if is_ajax:
            pending = newspaper.article_invites.filter(used=False)
            pending_info = []
            for inv in pending:
                invite_url = request.build_absolute_uri(
                    reverse("core:accept_newspaper_invite", args=[str(inv.token)])
                )
                pending_info.append(
                    {"invite": inv, "invite_url": invite_url}
                )
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

    messages.info(
        request,
        "Use the inline modal on the newspaper page to create invites.",
    )
    return redirect(newspaper.get_absolute_url())


def accept_newspaper_invite(request, token):
    """Accept an invite identified by its token and add the user as a
    publisher for the newspaper.
    """
    invite = get_object_or_404(ArticleInvite, token=token, used=False)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('core:login')}?next={request.path}")

    if (
        invite.email and invite.email.lower() != request.user.email.lower()
    ):
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

    def test_func(self):
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

    def test_func(self):
        newspaper = self.get_object()
        return (
            self.request.user in newspaper.publishers.all()
            or self.request.user.is_superuser
        )


def search_publishers(request):
    """Return a partial HTML list of publishers matching the query.

    GET param: `q` (search query).
    """
    query = request.GET.get("q", "").strip()
    if query:
        publishers = Publisher.objects.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).distinct()
    else:
        publishers = Publisher.objects.all()

    return render(
        request,
        "core/partials/_publisher_list.html",
        {"publishers": publishers},
    )


def search_topics(request):
    """Return a partial HTML list of topics matching the query.

    GET param: `q` (search query).
    """
    query = request.GET.get("q", "").strip()
    if query:
        topics = Topik.objects.filter(name__icontains=query).distinct()
    else:
        topics = Topik.objects.all()

    return render(
        request,
        "core/partials/_topic_list.html",
        {"topics": topics},
    )


def search_newspapers(request):
    """Return a partial HTML list of newspapers matching the query.

    GET param: `q` (search query).
    """
    query = request.GET.get("q", "").strip()
    if query:
        newspapers = NewsPaper.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(topic__name__icontains=query)
        ).distinct()
    else:
        newspapers = NewsPaper.objects.all()

    return render(
        request,
        "core/partials/_newspaper_list.html",
        {"newspapers": newspapers},
    )


def register(request):
    """Register a new publisher and send email verification link."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = EmailVerificationToken.objects.create(user=user)
            verify_url = request.build_absolute_uri(
                reverse("core:verify_email", args=[str(token.token)])
            )

            print(f"Verification URL (send via email): {verify_url}")
            send_mail(
                subject="Verify your email",
                message=(
                    f"Please verify your email by visiting: {verify_url}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

            return render(
                request,
                "registration/verification_sent.html",
                {"email": user.email},
            )
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def verify_email(request, token):
    """Verify an email using a token and activate the user."""
    obj = get_object_or_404(EmailVerificationToken, token=token)

    user = obj.user
    user.is_email_verified = True
    user.is_active = True

    user.save()
    obj.delete()

    return render(
        request,
        "registration/verification_success.html",
        {"user": user},
    )


def logout_view(request):
    """Confirmation (GET) and POST logout view.

    GET: show confirmation page asking the user to confirm logout.
    POST: perform logout, add a message, and redirect to index.
    """
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("core:index")

    return render(request, "registration/logout_confirm.html")
