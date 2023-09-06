from django.contrib.sitemaps import Sitemap
from .models import Post

'''We have defined a custom sitemap by inheriting the Sitemap class
of the sitemaps module.'''
class PostSitemap(Sitemap):

 changefreq = 'weekly' # changefreq and priority both indicates the change frequency of the post pages and their relevance in your website (the maximum value is 1)
 
 priority = 0.9
 
 
 '''The items() method returns the QuerySet of objects to include in
this sitemap. By default, Django calls the get_absolute_url()
method on each object to retrieve its URL'''
 def items(self):
     return Post.published.all()
 
 def lastmod(self, obj):
     return obj.updated
 '''The lastmod method receives each object returned by items() and
returns the last time the object was modified.Both the changefreq and priority a
'''
