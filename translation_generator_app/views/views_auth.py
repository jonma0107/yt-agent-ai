"""
Authentication views for the Content Analysis API.

Session-based auth using Django's built-in User model:
- Superuser creates additional users via `createsuperuser` or /admin/.
- Clients log in via POST /login/ (session cookie) and call the
  protected endpoints with that cookie. POST /logout/ ends the session.
"""
import json
import logging
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout

from ..exceptions import InvalidDataException

logger = logging.getLogger(__name__)


class LoginView(View):
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
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Disable CSRF for this view (API clients don't send CSRF tokens)."""
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                raise InvalidDataException("Invalid JSON data")

            username = (data.get('username') or '').strip()
            password = data.get('password') or ''

            if not username or not password:
                raise InvalidDataException("Fields 'username' and 'password' are required")

            user = authenticate(request, username=username, password=password)
            if user is None:
                logger.warning(f"Failed login attempt for username: {username}")
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

            if not user.is_active:
                return JsonResponse({'error': 'User account is disabled'}, status=403)

            login(request, user)
            logger.info(f"User logged in: {username}")
            return JsonResponse({'username': user.username}, status=200)

        except InvalidDataException as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception:
            logger.exception("Unexpected error during login")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    def get(self, request):
        """Handle GET request - return method not allowed."""
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)


class LogoutView(View):
    """
    Log the current user out and end the session.

    Endpoint: POST /logout/
    Response (200): {"message": "Logged out"}
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Disable CSRF for this view (API clients don't send CSRF tokens)."""
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        username = request.user.username if request.user.is_authenticated else None
        logout(request)
        logger.info(f"User logged out: {username}")
        return JsonResponse({'message': 'Logged out'}, status=200)

    def get(self, request):
        """Handle GET request - return method not allowed."""
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
