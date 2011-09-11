import os, sys

project = 'fgsales'

sys.stdout = sys.stderr
dir = os.path.dirname(__file__)
sys.path.append(dir)
sys.path.append(os.path.join(dir, project))
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project

from django.core.handlers import wsgi
application = wsgi.WSGIHandler()

