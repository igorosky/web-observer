from rest_framework.permissions import  IsAuthenticated

class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        from .exception_handler import NotAuthenticatedError
        if 'sessionid' not in request.COOKIES:
            raise NotAuthenticatedError()
        return super().has_permission(request, view)