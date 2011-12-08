import os
import urllib
import urllib2
import re

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

from PIL import Image
from BeautifulSoup import BeautifulSoup

base_initial_data = {
    'footer_text': 'this is default footer text',
}

initial_data = {
    'normal': dict(base_initial_data),
    'server': dict(base_initial_data),
}

server_images = (
    ('back', 700),
    ('feature', 350),
    ('front', 700),
)

normal_images = (
    ('feature', 350),
    (None, 240),
)

class ListingForm(forms.Form):
    system_id = forms.SlugField(label='Directory Name',
        help_text='Use something unique, such as System ID')
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
        system_id = self.cleaned_data['system_id']
        local_path = os.path.join(settings.MEDIA_ROOT, 'image', 'system',
            system_id)
        remote_path = os.path.join(settings.BASE_IMAGES_URL,
            '~%s' % self.cleaned_data['username'], 'system', system_id)

        try:
            os.makedirs(local_path)
        except OSError:
            pass

        if self.listing_type == 'server':
            self.images = fetch_server_images(remote_path, local_path,
                self.cleaned_data['refresh_images'])
        else:
            self.images = fetch_normal_images(remote_path, local_path,
                self.cleaned_data['refresh_images'])

    @property
    def image_url(self):
        return os.path.join(settings.MEDIA_URL, 'image', 'system',
            self.cleaned_data['system_id'])


def fetch_server_images(remote_path, local_path, refresh):
    for fn, width in server_images:
        remote_filename = os.path.join(remote_path, '%s.JPG' % fn)
        local_filename = os.path.join(local_path, '%s.jpg' % fn)

        if not os.path.exists(local_filename) or refresh:
            fetch_single_image(remote_filename, local_filename, width)

def fetch_normal_images(remote_path, local_path, refresh):
    index = BeautifulSoup(urllib2.urlopen(remote_path))
    widths = dict(normal_images)
    images = []

    for a in index('img', alt='[IMG]'):
        fn = a.next.find('a')['href']

        if fn.lower() == 'feature.jpg':
            width = widths['feature']
        else:
            width = widths[None]

        remote_filename = os.path.join(remote_path, fn)
        local_filename = os.path.join(local_path, fn.lower())

        if fn.lower() != 'feature.jpg':
            images.append(os.path.splitext(fn.lower())[0])

        if not os.path.exists(local_filename) or refresh:
            fetch_single_image(remote_filename, local_filename, width)

    return images

def fetch_single_image(remote_filename, local_filename, width):
    print remote_filename
    print local_filename
    print width
    info = None
    try:
        _, info = urllib.urlretrieve(remote_filename, local_filename)
    except:
        pass

    if not info or info.gettype() != 'image/jpeg':
        urllib.urlretrieve(remote_filename.lower(), local_filename)

    thumb_filename = os.path.join('%s_thumb.jpg' % os.path.splitext(
        local_filename)[0])
    try:
        original = Image.open(local_filename)
        original.thumbnail((width, 1000), Image.ANTIALIAS)
        original.save(thumb_filename, 'JPEG')
    except IOError:
        os.remove(local_filename)


