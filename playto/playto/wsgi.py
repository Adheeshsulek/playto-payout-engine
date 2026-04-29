import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto.playto.settings')

application = get_wsgi_application()

#  AUTO MIGRATE (FREE PLAN FIX)
from django.core.management import call_command

try:
    call_command('migrate')
except Exception as e:
    print("Migration error:", e)