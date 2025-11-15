"""
WSGI config for reform project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reform.settings')

application = get_wsgi_application()

