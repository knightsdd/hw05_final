from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls.base import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import make_paginator


def index(request):

    posts = Post.objects.all()
    page_obj = make_paginator(posts, request, settings.RECORDS_PER_PAGE)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = make_paginator(posts, request, settings.RECORDS_PER_PAGE)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    selected_user = get_object_or_404(User, username=username)
    posts = selected_user.posts.all()
    count = selected_user.posts.count()
    page_obj = make_paginator(posts, request, settings.RECORDS_PER_PAGE)
    following = False
    if request.user.is_authenticated:
        following = selected_user.following.filter(user=request.user).exists()
    template = 'posts/profile.html'
    context = {
        'selected_user': selected_user,
        'count': count,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    selected_post = get_object_or_404(Post, pk=post_id)
    post_preview = selected_post.text[:30]
    count = selected_post.author.posts.count()
    template_name = 'posts/post_detail.html'
    form_comment = CommentForm()
    comments = selected_post.comments.all()
    context = {
        'post': selected_post,
        'preview': post_preview,
        'count': count,
        'form_comment': form_comment,
        'comments': comments
    }

    return render(request, template_name, context)


@login_required
def post_create(request):
    """Add new post."""

    template_name = 'posts/create_post.html'

    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            succses_url = reverse_lazy(
                'posts:profile',
                args=[request.user.username]
            )

            return redirect(succses_url)

        return render(request, template_name, {'form': form})

    form = PostForm()

    context = {
        'form': form
    }
    return render(request, template_name, context)


@login_required
def post_edit(request, post_id):
    """Edit post."""

    edited_post = get_object_or_404(Post, pk=post_id)

    if edited_post.author != request.user:
        return redirect(reverse_lazy('posts:post_detail', args=[post_id]))

    template_name = 'posts/create_post.html'

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edited_post
    )

    if form.is_valid():
        form.save()
        return redirect(reverse_lazy('posts:post_detail', args=[post_id]))

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }

    return render(request, template_name, context)


@login_required
def add_comment(reqest, post_id):
    """Add a comment to the post."""

    commented_post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(reqest.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = reqest.user
        comment.post = commented_post
        comment.save()

    return redirect(reverse('posts:post_detail', args=[post_id]))


@login_required
def follow_index(request):
    """View subscriptions."""

    user = User.objects.get(username=request.user.username)
    follows = user.follower.all()
    authors = []
    for f in follows:
        authors.append(f.author)
    posts = Post.objects.filter(author__in=authors)
    page_obj = make_paginator(posts, request, settings.RECORDS_PER_PAGE)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Add subscription."""

    author = get_object_or_404(User, username=username)
    if author==request.user:
        return redirect(reverse('posts:profile', args=[username]))
    if Follow.objects.filter(user=request.user).filter(author=author).exists():
        return redirect(reverse('posts:profile', args=[username]))

    Follow.objects.create(
        user=request.user,
        author=author
    )

    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    """Remove subscription."""

    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user).filter(author=author).delete()

    return redirect(reverse('posts:profile', args=[username]))
