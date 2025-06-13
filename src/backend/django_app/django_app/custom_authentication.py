from rest_framework.permissions import IsAuthenticated

class CustomIsAuthenticated(IsAuthenticated):
    """
    Custom authentication permission class for session-based authentication.

    - Allows all `OPTIONS` requests (used by CORS preflight).
    - Raises NotAuthenticatedError if 'sessionid' cookie is missing.
    - Otherwise defers to DRF's IsAuthenticated logic.
    """
    def has_permission(self, request, view):
        from .exception_handler import NotAuthenticatedError

        if request.method == 'OPTIONS':
            return True

        if 'sessionid' not in request.COOKIES:
            raise NotAuthenticatedError()

        return super().has_permission(request, view)
