from django.urls import path, include

from . import views


app_name = "core"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),

    path(
        "search/publishers/",
        views.SearchPublishersView.as_view(),
        name="search_publishers",
    ),
    path(
        "search/topics/",
        views.SearchTopicsView.as_view(),
        name="search_topics",
    ),
    path(
        "search/newspapers/",
        views.SearchNewspapersView.as_view(),
        name="search_newspapers",
    ),



    path("topics/", views.TopikListView.as_view(), name="topics_list"),
    path("topics/create/", views.TopikCreateView.as_view(), name="topics_create"),
    path("topics/<int:pk>/edit/", views.TopikUpdateView.as_view(), name="topic_edit"),

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
        views.CreateNewspaperInviteView.as_view(),
        name="newspaper_create_invite",
    ),
    path(
        "newspapers/invite/<uuid:token>/accept/",
        views.AcceptNewspaperInviteView.as_view(),
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

    path("accounts/", include("django.contrib.auth.urls")),
]
