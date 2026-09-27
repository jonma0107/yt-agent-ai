from django.urls import path
from .views import ContentAnalysisView, generate_report, LoginView, LogoutView


urlpatterns = [
    # Authentication (session-based, Django User model)
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Content analysis (requires login)
    path('generate-report/', ContentAnalysisView.as_view(), name='generate-report'),

    # Legacy function-based view (for backwards compatibility)
    # path('generate-report', generate_report, name='generate-report-legacy'),
]
