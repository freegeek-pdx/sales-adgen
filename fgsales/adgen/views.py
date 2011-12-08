from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from adgen import forms

def generate_listing(request, listing_type):
    username = request.COOKIES.get('username', '')
    form = forms.ListingForm(request.POST or None,
        listing_type=listing_type,
        username=username
    )
    context = {'form': form}

    if request.POST and form.is_valid():
        form.fetch_images()
        output_context = dict(form.cleaned_data,
            image_url=request.build_absolute_uri(form.image_url),
            system_images=form.images,
        )
        context['output'] = render_to_string(
            'adgen/listing_%s.html' % listing_type,
            output_context, RequestContext(request))
        username = form.cleaned_data['username']

    response = render_to_response('adgen/generate_listing.html', context,
        RequestContext(request))

    if username:
        response.set_cookie('username', username)

    return response
