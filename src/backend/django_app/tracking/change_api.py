from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import requests

from django_app.exception_handler import CustomAPIException

from observing.web_observer_api import Notification
from .models import TrackedElement, ElementChange, UserElementUpdate, Observer
from rest_framework.response import Response

from .models import UserTrackedWebsites
from .serializers import ElementIDSerializer
from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException



def register_change(notification:Notification):
    print(notification.image)
    siteId = Observer.objects.get(id=notification.observer_id).site.siteId
    textChange = notification.new_value
    imageChangeUrl = notification.image
    error = notification.error
    try:
            user_id = UserTrackedWebsites.objects.get(website_id=siteId).user.id
            element_id = TrackedElement.objects.get(website_id=siteId).id
            tracked_element = TrackedElement.objects.get(id=element_id)
            site = tracked_element.website
    except ObjectDoesNotExist:
            raise CustomAPIException(status_code=404, message="Do not have access to this element", detail={})

    with transaction.atomic():
            element_change = ElementChange.objects.create(
                element_id=element_id,
                content="maybe it is to remove",
                textChange = textChange,
                imageChangeUrl = imageChangeUrl,
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
