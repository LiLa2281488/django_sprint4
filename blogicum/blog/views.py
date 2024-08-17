from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404, render, redirect

from django.utils import timezone

from django.http import Http404

from django.core.exceptions import PermissionDenied

from blog import models, forms


def index(request):
    template = 'blog/index.html'
    post_list = (models.Post.published.select_related(
        'author',
        'location',
        'category'
    ).order_by('-pub_date'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(
        models.Post, pk=post_id,
    )
    if ((not post.is_published
         or not post.category.is_published
         or post.pub_date > timezone.now()) and request.user != post.author):
        raise Http404
    context = {
        'post': post,
        'form': forms.CommentForm(),
        'comments': models.Comment.objects.filter(post=post)}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        models.Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'post_list': post_list,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = forms.CreatePostForm(request.POST)
        if form.is_valid():
            author = models.User.objects.get(username=request.user.username)
            existing_post = models.Post.objects.filter(
                title=form.cleaned_data['title']
            ).first()
            if existing_post:
                pass
            else:
                post = form.save(commit=False)
                post.author = author
                post.pub_date = timezone.now()
                post.image = request.FILES.get('image')
                post.save()
                return redirect('blog:profile', username=author.username)
    else:
        form = forms.CreatePostForm()
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_post(request, post_id):
    post = get_object_or_404(models.Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    else:
        if request.method == 'POST':
            form = forms.EditPostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('blog:post_detail', post_id=post_id)
        else:
            form = forms.EditPostForm(instance=post)
        context = {'form': form}
        return render(request, 'blog/create.html', context)


def get_profile(request, username):
    profile = get_object_or_404(models.User, username=username)
    user_posts = models.Post.objects.filter(
        author=profile.id
    ).order_by('-pub_date')
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'user_posts': user_posts,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    user = get_object_or_404(models.User, username=username)
    if request.method == 'POST':
        form = forms.UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
    else:
        form = forms.UserEditForm(instance=user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(models.Post, pk=post_id)
    form = forms.CommentForm(request.POST)
    context = {'form': form, 'post': post}
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            post.comment_count += 1
            post.save()
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(models.Post, pk=post_id)
    if request.user == post.author:
        post.delete()
    return redirect('blog:index')


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(models.Post, pk=post_id)
    comment = get_object_or_404(models.Comment, pk=comment_id)
    if request.user != comment.author:
        raise PermissionDenied
    form = forms.CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    context = {'form': form,
               'post': post,
               'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(models.Post, pk=post_id)
    comment = get_object_or_404(models.Comment, pk=comment_id)
    if request.user != comment.author:
        raise PermissionDenied
    if request.method == 'POST':
        post.comment_count -= 1
        post.save()
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
