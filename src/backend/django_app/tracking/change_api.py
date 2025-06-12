from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import requests
from django_app.exception_handler import CustomAPIException
from observing.web_observer_api import Notification
from .gotify import send_gotify_message
from .models import TrackedElement, ElementChange, UserElementUpdate, Observer, GotifyInfo
from rest_framework.response import Response
from .models import UserTrackedWebsites
from .serializers import ElementIDSerializer
from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException



from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import requests

def register_change(notification: Notification):
    site_id = Observer.objects.get(id=notification.observer_id).site.siteId
    text_change = notification.new_value
    image_change_url = notification.image
    error = notification.error

    try:
        user_id = UserTrackedWebsites.objects.get(website_id=site_id).user.id
        element = TrackedElement.objects.get(website_id=site_id)
        element_id = element.id
        site = element.website
    except ObjectDoesNotExist:
        raise CustomAPIException(status_code=404, message="Do not have access to this element", detail={})

    try:
        last_change = ElementChange.objects.filter(element_id=element_id).latest("detectedAt")
        if last_change.textChange == text_change and text_change is not None:
            return
    except ElementChange.DoesNotExist:
        pass
    with transaction.atomic():
        element_change = ElementChange.objects.create(
            element_id=element_id,
            textChange=text_change,
            imageChangeUrl=image_change_url,
        )

        try:
            response = requests.get(site.siteUrl, timeout=5)
            status_code = response.status_code
        except requests.RequestException:
            status_code = 501

        UserElementUpdate.objects.create(
            user_id=user_id,
            element_id=element_id,
            website_id=site.siteId,
            statusCode=status_code,
            updateTime=element_change.detectedAt,
            error=error
        )

        gotify_entries = GotifyInfo.objects.filter(user_id=user_id)
        for entry in gotify_entries:
            if image_change_url:
                send_gotify_message(
                    url=entry.url,
                    token=entry.token,
                    title="Message from NotifyMe!",
                    message="You have new photo update on NotifyMe, check this!",
                )
            else:
                send_gotify_message(
                    url=entry.url,
                    token=entry.token,
                    title="Message from NotifyMe!",
                    message=notification.new_value,
                )

