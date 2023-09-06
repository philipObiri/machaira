from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count


# Create your views here.


# A functional based view to display the list of all posts.
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    # If a tag has been added to a post
    if tag_slug:
        # filter and show the posts by their respective tags
        tag = get_object_or_404(
            Tag, slug=tag_slug
        )  # There is a many to many relationship between the tags and posts
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(
        post_list, 3
    )  # We instantiate the Paginator class with the number of objects to return per page. We will display three posts per page.

    page_number = request.GET.get(
        "page", 1
    )  # We retrieve the page GET HTTP parameter and store it in the page_number variable. This parameter contains the requested page number.
    # If the page parameter is not in the GET parameters of the request, we use the default value 1 to load the first page of results.
    try:
        posts = paginator.page(page_number)

    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)

    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


# A functional based view to display the details of a single post.
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # List of active comments for this post
    # A QuerySet to retrieve all active comments for each active post.:
    """
     This queryset was built using the post object. Instead of building the the queryset for the comment model directly,
     we leverage the post object to retrieve the related Comment objects
     We use the comments manager for the related Comment objects that we previously defined in the Comment model, using the related_name= 'comments' 
    """
    comments = post.comments.filter(active=True)

    # Form for users to comment :
    form = CommentForm()  # This creates an instance of the comment form

    # A List of similar posts
    post_tags_ids = post.tags.values_list(
        "id", flat=True
    )  # retrieve a python list of ids for the tags of the current post and set the ids to flat to get single digits instead of tuples
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(
        id=post.id
    )  # Get all the posts that contain any of tags fetched, excluding the posts itself
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[
        :4
    ]  # generate a calculated field{"-same_tags"} that contains the number of tags shared with all the tags queried
    # Retrieve and order the results by the number of shared tags (in descending order) and by publish to display recent posts first for posts with the same shared number of  tags
    # Slice the results to retrieve only the first four posts

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


# This is a Class based View that equally retrieves the list of all posts created
class PostListView(ListView):
    """
    Alternative post list view
    """

    # Here we didn't use the model attribute because the view would automatically fetch the model we give it and assign a default objects manager to it .
    queryset = (
        Post.published.all()
    )  # Here We use the queryset attribute to point the model to a custom manager we declared (a class called PublishedManager on our Post Model )
    context_object_name = "posts"  # the default name of context variables is objects . But we want to change it to 'posts'
    paginate_by = 3  # We define the pagination of results with paginate_by,returning three objects per page.
    template_name = "blog/post/list.html"  # We use a custom template to render the page with template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        # Form was submitted (that means the user has clicked the submit/send button)
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(subject, message, "philipobiri3.1@gmail.com", [cd["to"]])
            sent = True

    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


@require_POST  # restrict the HTTP method allowed for this view to a POST Method .
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    comment = None

    # A comment was posted
    form = CommentForm(data=request.POST)

    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)

        # Assign the post to the comment
        comment.post = post

        # Save the comment to the database
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


"""
First, we instantiate the SearchForm form:
To
check whether the form is submitted, we look for query parameter in the request.GET dictionary.
We send the form using the GET method instead of the POST so that the resulting URL includes
the query parameter and is easy to share. 
When the form is submitted, we instantiate it with the submitted GET data and verify that the form data is valid.

If thr form is valid we search for published posts with a custom SearchVector  instance built with the title and body fields.   
"""


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            # search_vector = SearchVector('title', 'body')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector,search_query)).filter(search_query).order_by('-similarity')
            results = Post.published.annotate(
                search=SearchVector("title", "body")
            ).filter(search=query)
            # results = Post.published.annotate(
            #     similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )
