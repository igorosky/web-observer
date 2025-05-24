from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import requests

from django_app.exception_handler import CustomAPIException
from .models import TrackedElement,ElementChange, UserElementUpdate
from rest_framework.response import Response

from .models import UserTrackedWebsites
from .serializers import ElementIDSerializer
from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException

#ofc in the future only in auth area
# by websiteid -> KEY (TrackedElement)
def get_element_id(user, site_id):
    if not site_id:
        raise CustomAPIException(status_code=400, message="Missing site id", detail={})
    if not UserTrackedWebsites.exists_site_for_user(site_id, user.id):
        raise CustomAPIException(status_code=401, message="No permission to get this site", detail={})

    serializer = ElementIDSerializer(data={"siteId": site_id})
    serializer = validate_or_raise(serializer, status_code=404, message="Search for this site failed")

    return serializer.validated_data["element_id"]


#change can be null but required
class ElementChangeHandler:
    @staticmethod
    def register_change(user, element_id, content, change):
        try:
            tracked_element = TrackedElement.objects.select_related('website').get(id=element_id)
            site = tracked_element.website
            user_website = UserTrackedWebsites.objects.get(website=site, user=user)
        except ObjectDoesNotExist:
            raise CustomAPIException(status_code=404, message="Do not have access to this element", detail={})

        with transaction.atomic():
            element_change = ElementChange.objects.create(
                element_id=element_id,
                content=content,
                change=change,
            )

            try:
                response = requests.get(site.siteUrl, timeout=5)
                status_code = response.status_code
            except requests.RequestException:
                status_code = 501

            UserElementUpdate.objects.create(
                user_id=user.id,
                element_id=element_id,
                website_id=site.siteId,
                statusCode=status_code,
                updateTime=element_change.detectedAt
            )

        return element_change
# test in views.py show how to use this
#element_change = ElementChangeHandler.register_change(
#    user=current_user(request.user),
#    element_id=get_element_id,() this is key from other table where are tracked elements stored
#    content="new HTML here",
#    change="diff here or ' '  "
#)