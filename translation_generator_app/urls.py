from django.urls import path
from .views import ContentAnalysisView, generate_report


urlpatterns = [
    path('generate-report/', ContentAnalysisView.as_view(), name='generate-report'),
    
    # Legacy function-based view (for backwards compatibility)
    # path('generate-report', generate_report, name='generate-report-legacy'),
]