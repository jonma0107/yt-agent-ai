from django.urls import path
from .views import TranslationGeneratorView, generate_translation


urlpatterns = [
    # Class-based view (recommended)
    path('generate-translation/', TranslationGeneratorView.as_view(), name='generate-translation'),
    
    # Legacy function-based view (for backwards compatibility)
    # path('generate-translation', generate_translation, name='generate-translation-legacy'),
]
