from django import forms

from .models import Post, User, Comment


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'location', 'category', 'image']


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'location', 'category', 'image']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']

