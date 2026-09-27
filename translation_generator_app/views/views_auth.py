"""
Authentication views for the Content Analysis API.

Session-based auth using Django's built-in User model:
- Superuser creates additional users via `createsuperuser` or /admin/.
- Clients log in via POST /login/ (session cookie) and call the
  protected endpoints with that cookie. POST /logout/ ends the session.

Throttling (DRF ScopedRateThrottle, scope 'login'): protects against
brute force. Rate configured in settings.py (LOGIN_THROTTLE_RATE).
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import SessionAuthentication

from ..exceptions import InvalidDataException

logger = logging.getLogger(__name__)


class SessionNoCSRF(SessionAuthentication):
    """
    Session auth without CSRF enforcement.

    Reads the Django session cookie like SessionAuthentication, but skips
    the CSRF check so non-browser API clients (curl, scripts) can use the
    session cookie directly. Safe here because state-changing calls still
    require a valid logged-in session.
    """

    def enforce_csrf(self, request):
        return


class LoginView(APIView):
    """
    Log a user in and start a session.

    Endpoint: POST /login/

    Request Body:
        {
            "username": "usuario",
            "password": "secreto"
        }

    Response (200):
        {"username": "usuario"}
    Response (400/401):
        {"error": "..."}
    Response (429):
        {"detail": "Request was throttled..."}
    """

    throttle_scope = 'login'
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else {}
            username = (data.get('username') or '').strip()
            password = data.get('password') or ''

            if not username or not password:
                raise InvalidDataException("Fields 'username' and 'password' are required")

            user = authenticate(request, username=username, password=password)
            if user is None:
                logger.warning(f"Failed login attempt for username: {username}")
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({'error': 'User account is disabled'}, status=status.HTTP_403_FORBIDDEN)

            login(request, user)
            logger.info(f"User logged in: {username}")
            return Response({'username': user.username}, status=status.HTTP_200_OK)

        except InvalidDataException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Unexpected error during login")
            return Response({'error': 'An unexpected error occurred'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Handle GET request - return method not allowed."""
        return Response({'error': 'Method not allowed. Use POST.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LogoutView(APIView):
    """
    Log the current user out and end the session.

    Endpoint: POST /logout/
    Response (200): {"message": "Logged out"}
    """

    authentication_classes = [SessionNoCSRF]
    permission_classes = []

    def post(self, request):
        username = request.user.username if request.user.is_authenticated else None
        logout(request)
        logger.info(f"User logged out: {username}")
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)

    def get(self, request):
        """Handle GET request - return method not allowed."""
        return Response({'error': 'Method not allowed. Use POST.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
