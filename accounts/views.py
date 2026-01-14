from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
)

from django.shortcuts import get_object_or_404

from .models import Publisher
from .forms import PublisherForm, RegistrationForm
from core.models import NewsPaper


class PublisherListView(ListView):
    model = Publisher
    template_name = "core/publisher_list.html"
    context_object_name = "publishers"


class PublisherCreateView(CreateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "core/publisher_form.html"
    success_url = reverse_lazy("accounts:publishers_list")


class PublisherDetailView(DetailView):
    model = Publisher
    template_name = "core/publisher_detail.html"
    context_object_name = "publisher"


class PublisherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "core/publisher_form.html"
    success_url = reverse_lazy("accounts:publishers_list")

    def test_func(self) -> bool:
        obj = self.get_object()
        return self.request.user == obj or self.request.user.is_superuser


class PublisherArticlesView(ListView):
    model = NewsPaper
    template_name = "core/publisher_articles.html"
    context_object_name = "newspapers"

    def get_queryset(self):
        publisher_pk = self.kwargs.get("pk")
        publisher = get_object_or_404(Publisher, pk=publisher_pk)
        return NewsPaper.objects.filter(publishers=publisher).order_by("-published_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["publisher"] = get_object_or_404(Publisher, pk=self.kwargs.get("pk"))
        return ctx


class RegisterView(CreateView):
    model = Publisher
    form_class = RegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("accounts:login")


class AppLogoutView(LogoutView):
    template_name = "registration/logout_confirm.html"
    next_page = reverse_lazy("index")
