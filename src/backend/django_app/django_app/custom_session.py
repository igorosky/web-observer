from rest_framework.authentication import SessionAuthentication
from django.contrib.sessions.models import Session
from django.utils.timezone import now


class CustomSessionAuthentication(SessionAuthentication):
    """
    Custom session-based authentication class that adds more precise error handling.

    Exceptions raised:
    - NotAuthenticatedError: no session key present.
    - InvalidSessionError: session key does not exist in the database.
    - SessionExpiredError: session exists but has expired.
    - UserInactiveError: user is inactive or could not be authenticated.
    """
    def authenticate(self, request):
        from django_app.exception_handler import NotAuthenticatedError, InvalidSessionError, SessionExpiredError, \
            UserInactiveError

        session_key = request.COOKIES.get('sessionid')
        if not session_key:
            if request.COOKIES.get('was_logged_in') == '1':
                raise SessionExpiredError()
            raise NotAuthenticatedError()
        try:
            session = Session.objects.get(session_key=session_key)
        except Session.DoesNotExist:
            raise InvalidSessionError()  # 401

        if session.expire_date < now():
            raise SessionExpiredError() # 403

        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            raise UserInactiveError()  # 403

        return user_auth_tuple
