from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.cache import cache_page

from .models import Follow, Post, Group, User
from .forms import PostForm, CommentForm


def pagination_function(request, object):
    paginator = Paginator(object, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    result = paginator.get_page(page_number)
    return result


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all()
    page_obj = pagination_function(request, post_list)
    context = {
        "page_obj": page_obj,
        "index": True,
    }
    template = "posts/index.html"
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination_function(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    template = "posts/group_list.html"
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = pagination_function(request, posts)
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists(),
    }
    template = "posts/profile.html"
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
        "form": CommentForm(),
        "comments": post.comments.all(),
    }
    template = "posts/post_detail.html"
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:profile", request.user.username)
    context = {
        "form": form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def delete_post(request, post_id):
    post_to_delete = get_object_or_404(Post, id=post_id)
    post_to_delete.delete()
    return redirect("posts:profile", request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        "form": form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        "page_obj": pagination_function(request, posts),
        "follow": True,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect("posts:follow_index")
    Follow.objects.get_or_create(
        user=request.user,
        author=author,
    )
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    unsubscribe_author = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    if unsubscribe_author.exists():
        unsubscribe_author.delete()
    return redirect("posts:follow_index")
