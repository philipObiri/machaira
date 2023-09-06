from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# The tags manager will allow us to add, retrieve, and remove tags from Post objects.


# Create your models here.
""" The get_queryset() method of a manager returns the QuerySet
that will be executed. We have overridden this method to build a
custom QuerySet that filters posts by their status and returns a
successive QuerySet that only includes posts with the PUBLISHED
status.
We define a custom model manager for the Post model below:"""


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    tags = TaggableManager() # This allows us to add retrieve and remove tags fromfrom the Posts
    body = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )

    """You can use the Meta attribute default_manager_name to specify a different default manager name. If no manager is defined in the model, Django automatically creates an 'objects' default manager for it. If 
    you decare any custom managers for your model but you still want to keep the objects model manager as well, you have to add it explicitly to your model as well.
    In the code below, we have added the default objects manager and the published custom manager(Defined above as PublishedManager) to the Post model"""
    objects = models.Manager()  # The default manager.
    published = (
        PublishedManager()
    )  # Our custom manager. This manager helps us to return a query set of all published posts (filter happens by the publish status).

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]
