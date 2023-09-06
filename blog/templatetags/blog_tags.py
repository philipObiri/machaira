from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Post


register = template.Library()  # In other to create custom template tags, we need to assign a register variable to a method of the template class called Library 
"""
------- CREATING CUSTOM TEMPLATE TAGS -------
There are two kinds of template tags: 1. Simple tags and 2.Inclusion tags 
In this code , We create a simple template tag that returns the number of posts published in the blog.
Each module that contains template tags needs to define a variable
called register to be a valid tag library. This variable is an instance
of template.Library, and it’s used to register the template tags
and filters of the application.
"""
@register.simple_tag
def total_posts():
    return Post.published.count()  #this returns all the Posts published using the count() method
    

"""We will create another tag to display the latest posts in the sidebar of
the blog. This time, we will implement an inclusion tag. Using an
inclusion tag, you can render a template with context variables
returned by your template tag.
"""
@register.inclusion_tag('blog/post/latest_posts.html') #This allows us to render the number latest posts in the top right side bar. 
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}




# This tag simply shows or renders out the posts with the most comments. 
@register.simple_tag
def get_most_commented_posts(count=5):
 return Post.published.annotate(     # 'Annotate is a function of Django Queryset used to aggregate the total number of comments for each post
                                
 total_comments=Count('comments')    #Use the Count aggregation function to store the number of comments in the computed total_comments field for each Post object
 
 ).order_by('-total_comments')[:count]  #You order the QuerySet by the computed field in descending order. You also provide an optional count variable to limit the total number of objects returned.


@register.filter(name='markdown')
def markdown_format(text):
 return mark_safe(markdown.markdown(text))




