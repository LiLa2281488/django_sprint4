from .models import Category
from .models import Post
from .models import Location
from django.contrib import admin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = "pub_date"
    list_display = ["title", "author", "pub_date"]
    search_fields = ["title__startswith", "author__username"]
    ordering = ["-pub_date"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "post_count"]
    search_fields = ["title__istartswith"]

    def post_count(self, name):
        counter = Post.objects.filter(category=name).count()
        return counter


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name__startswith']
    list_display = ['name', 'post_count']

    def post_count(self, name):
        counter = Post.objects.filter(
            location=name
        ).count()
        return counter
