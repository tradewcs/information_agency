from django.urls import path, include

from . import views


app_name = "accounts"

urlpatterns = [
    path(
        "publishers/",
        views.PublisherListView.as_view(),
        name="publishers_list",
    ),
    path(
        "publishers/create/",
        views.PublisherCreateView.as_view(),
        name="publishers_create",
    ),
    path(
        "publishers/<int:pk>/",
        views.PublisherDetailView.as_view(),
        name="publisher_detail",
    ),
    path(
        "publishers/<int:pk>/edit/",
        views.PublisherUpdateView.as_view(),
        name="publisher_edit",
    ),
    path(
        "publishers/<int:pk>/articles/",
        views.PublisherArticlesView.as_view(),
        name="publisher_articles",
    ),

    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.AppLogoutView.as_view(), name="logout"),
    path("", include("django.contrib.auth.urls")),
]
