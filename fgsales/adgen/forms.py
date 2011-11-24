import os
import urllib
import re

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

from PIL import Image

base_initial_data = {
    'footer_text': 'this is default footer text',
}

initial_data = {
    'normal': dict(base_initial_data),
    'server': dict(base_initial_data),
}

images = {
    'normal': (
        ('back', 350),
        ('closeup', 240),
        ('front', 240),
    ),
    'server': (
        ('back', 700),
        ('closeup', 350),
        ('front', 700),
    )
}

class ListingForm(forms.Form):
    system_id = forms.SlugField(label='Directory Name', help_text='Use something unique, such as System ID')
    title = forms.CharField()
    subtitle = forms.CharField(required=False, help_text='Optional')
    price = forms.DecimalField(help_text='Don\'t include dollar sign')
    details = forms.CharField(widget=forms.Textarea,
        help_text='Enter one detail per line')
    additional_info = forms.CharField(widget=forms.Textarea)
    footer_text = forms.CharField(widget=forms.Textarea)
    username = forms.CharField()
    refresh_images = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.listing_type = kwargs.pop('listing_type')
        initial = initial_data[self.listing_type].copy()
        username = kwargs.pop('username', '')
        if username:
            initial['username'] = username
        super(ListingForm, self).__init__(
            initial=initial, *args, **kwargs)

    def clean_details(self):
        return mark_safe(
            '\n'.join('<li>%s</li>' % l for l in re.sub(
                r'\r\n|\r|\n', '\n', self.cleaned_data['details'].strip()
            ).split('\n') if l)
        )

    def fetch_images(self):
        return _fetch_images(self.listing_type,
            self.cleaned_data['system_id'],
            self.cleaned_data['username'],
            self.cleaned_data['refresh_images'])

    @property
    def image_url(self):
        return os.path.join(settings.MEDIA_URL, 'image', 'system',
            str(self.cleaned_data['system_id']))

def _fetch_images(listing_type, system_id, username,
        refresh_images=False):

    local_path = os.path.join(settings.MEDIA_ROOT, 'image', 'system',
        str(system_id))
    remote_path = os.path.join('http://127.0.0.1/~%s'%username, 'system', str(system_id))
    print remote_path

    if not os.path.exists(local_path):
        os.mkdir(local_path)

    for fn, width in images[listing_type]:
        local_filename = os.path.join(local_path, '%s.jpg' % fn)
        remote_filename = os.path.join(remote_path, '%s.JPG' % fn)

        if not os.path.exists(local_filename) or refresh_images:
            try:
                urllib.urlretrieve(remote_filename, local_filename)
            except IOError:
                urllib.urlretrieve(remote_filename.lower(), local_filename)

            thumb_filename = os.path.join(local_path, '%s_thumb.jpg' % fn)
            try:
                original = Image.open(local_filename)
                original.thumbnail((width, 1000), Image.ANTIALIAS)
                original.save(thumb_filename, 'JPEG')
            except IOError:
                os.remove(local_filename)

