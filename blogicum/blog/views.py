from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View
)

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post
from .utils import get_post_data

User = get_user_model()

POSTS_PER_PAGE = 10


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['post_id']})


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class IndexListView(ListView):
    model = Post
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return (
            self.model.objects
            .filter(is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now())
            .annotate(comment_count=Count('comment'))
            .order_by('-pub_date'))


class ProfileListView(ListView):
    model = Post
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count('comment'))
            .order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context

    def get_succes_url(self):
        return reverse_lazy(
            'profile', kwargs={self.request.user.username}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post_object = get_object_or_404(
            self.model.objects.select_related(
                'location', 'author', 'category'
            ), pk=self.kwargs['id'])
        if self.request.user == post_object.author:
            return get_object_or_404(
                self.model.objects.select_related(
                    'location', 'author', 'category'
                ), pk=self.kwargs['id'])
        return get_object_or_404(
            self.model.objects.select_related(
                'location', 'author', 'category'
            )
            .filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True), pk=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.kwargs['id']})


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)

        return (
            category.posts.select_related('location', 'author', 'category')
            .filter(is_published=True,
                    pub_date__lte=timezone.now())
            .annotate(comment_count=Count('comment'))
            .order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.values('id', 'title', 'description'),
            slug=self.kwargs['category_slug'])
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_post_data(kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj                 # проверить
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['post_id']})


class CommentMixin(LoginRequiredMixin, View):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass
