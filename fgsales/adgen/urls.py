from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('adgen.views',
    (r'^$', direct_to_template, {'template': 'adgen/choose_type.html'}),
    (r'^(?P<listing_type>\w+)/$', 'generate_listing'),
)

