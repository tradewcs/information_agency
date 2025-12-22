from django.urls import path, include

from . import views


app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),

    path(
        "search/publishers/",
        views.search_publishers,
        name="search_publishers",
    ),
    path(
        "search/topics/",
        views.search_topics,
        name="search_topics",
    ),
    path(
        "search/newspapers/",
        views.search_newspapers,
        name="search_newspapers",
    ),

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
        "publishers/<int:pk>/articles/",
        views.publisher_articles,
        name="publisher_articles",
    ),
    path(
        "publishers/<int:pk>/edit/",
        views.PublisherUpdateView.as_view(),
        name="publisher_edit",
    ),

    path(
        "topics/",
        views.TopikListView.as_view(),
        name="topics_list",
    ),
    path(
        "topics/create/",
        views.TopikCreateView.as_view(),
        name="topics_create",
    ),
    path(
        "topics/<int:pk>/edit/",
        views.TopikUpdateView.as_view(),
        name="topic_edit",
    ),

    path(
        "newspapers/",
        views.NewsPaperListView.as_view(),
        name="newspapers_list",
    ),
    path(
        "newspapers/create/",
        views.NewsPaperCreateView.as_view(),
        name="newspapers_create",
    ),
    path(
        "newspapers/<int:pk>/",
        views.NewsPaperDetailView.as_view(),
        name="newspaper_detail",
    ),
    path(
        "newspapers/<int:pk>/invite/",
        views.create_newspaper_invite,
        name="newspaper_create_invite",
    ),
    path(
        "newspapers/invite/<uuid:token>/accept/",
        views.accept_newspaper_invite,
        name="accept_newspaper_invite",
    ),
    path(
        "newspapers/<int:pk>/edit/",
        views.NewsPaperUpdateView.as_view(),
        name="newspaper_edit",
    ),
    path(
        "newspapers/<int:pk>/delete/",
        views.NewsPaperDeleteView.as_view(),
        name="newspaper_delete",
    ),

    path(
        "accounts/register/",
        views.register,
        name="register",
    ),
    path(
        "accounts/verify/<uuid:token>/",
        views.verify_email,
        name="verify_email",
    ),
    path(
        "accounts/logout/",
        views.logout_view,
        name="logout",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
]
