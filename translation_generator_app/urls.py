from django.urls import path
from .views import views_app


urlpatterns = [
    path('generate-translation', views_app.generate_translation, name='generate-translation'),
]
