import os
import django
import sys

def setup():
    # Add the project root to the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_translation.settings')
    # Initialize Django
    django.setup() 