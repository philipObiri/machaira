from django.contrib import admin
from .models import Post, Comment

# Register your models here.

# Below is the general way to register models on the admin site:
# admin.site.register(Post)


# Customizing the Admin Site :
@admin.register(
    Post
)  # this is a decorator that performs the same function as admin.site.register()
class PostAdmin(
    admin.ModelAdmin
):  # The admin.ModelAdmin is a built-in class that we inherit to customize the way each post should appear in the UI of our admin site
    list_display = [
        "title",
        "slug",
        "author",
        "publish",
        "status",
    ]  # list_display allows you to specify the fields you want to display from the model

    list_filter = [
        "status",
        "created",
        "publish",
        "author",
    ]  # list_filter attribute allows you to specify the fields by which you want to filter results when querying the model objects/instances

    search_fields = [
        "title",
        "body",
    ]  # A search bar has appears on the admin page, because we have defined a list of searchable fields using the search_fields attribute

    prepopulated_fields = {"slug": ("title",)}

    raw_id_fields = ["author"]

    date_hierarchy = "publish"

    ordering = ["status", "publish"]

    """
    -Just below the search bar, there are navigation links to navigate through a date hierarchy; this has been defined by the date_hierarchy attribute.
    
    -We can pre-populate the slug field with the input of the title field using the prepopulated_fields attribute. So as the user types the title of each post, the slug field is dynamically generated 
    
    -The author field is now displayed with a lookup widget, which can be much be better than a drop down select input when you have thousands of users. This is achieved with the raw_id_fields attribute.
    
    -We also order/ arrange the posts created by their status (Published")
    """


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]


admin.site.site_header = "Machaira Blog Admin"
admin.site.site_title = "Machaira Blog Admin Portal"
admin.site.index_title = "Welcome to Machaira"
