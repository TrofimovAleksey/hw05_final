from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    # Главная страница
    path("", views.index, name="index"),
    # Страница со списком сообществ
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    # Профайл пользователя
    path("profile/<str:username>/", views.profile, name="profile"),
    # Просмотр записи
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    # Create post
    path("create/", views.post_create, name="post_create"),
    # Delete post
    path("delete/<int:post_id>", views.delete_post, name="delete"),
    # Редактирование поста
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    # Создание комментария
    path(
        "posts/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    # Подписка и отписка
    path("follow/", views.follow_index, name="follow_index"),
    path(
        "profile/<str:username>/follow/",
        views.profile_follow,
        name="profile_follow",
    ),
    path(
        "profile/<str:username>/unfollow/",
        views.profile_unfollow,
        name="profile_unfollow",
    ),
]
