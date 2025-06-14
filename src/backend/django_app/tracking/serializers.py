import requests
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TrackedWebsite, UserTrackedWebsites, ElementChange, TrackedElement, UserElementUpdate, Observer, \
    ObserverInfo, GotifyInfo
from django.db import transaction, connection, IntegrityError
from django_app.utils import validate_or_raise
import os
from django_app.exception_handler import CustomAPIException
from .observers import load_observers_from_db, create_observer, make_settings_from_info
from .observers import  web_observer
from django.conf import settings
User = get_user_model()


class RegisterSiteWithObserverSerializer(serializers.ModelSerializer):
    """
    Handles full site registration along with element and observer setup.
    """
    elementName = serializers.CharField(write_only=True)
    selector = serializers.CharField(write_only=True)

    interval = serializers.CharField(write_only=True)
    observeImages = serializers.CharField(write_only=True)
#type -> siteType
#observe_images -> observeImages
    class Meta:
        model = TrackedWebsite
        fields = [
            "siteId", "siteName", "siteUrl", "siteDescription", "createdAt", "siteType",
            "selector", "elementName", "interval","observeImages"
        ]
        extra_kwargs = {
            'siteId': {'read_only': True},
            'createdAt': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user

        elementName = validated_data.pop('elementName')
        selector = validated_data.pop('selector')

        interval = validated_data.pop('interval')
        observeImages = validated_data.pop('observeImages')

        try:
            with transaction.atomic():
                site = TrackedWebsite.objects.create(
                    siteName=validated_data['siteName'],
                    siteUrl=validated_data['siteUrl'],
                    siteDescription=validated_data['siteDescription'],
                    siteType=validated_data['siteType']
                )

                UserTrackedWebsites.objects.create(
                    user_id=user.id,
                    website_id=site.siteId
                )

                TrackedElement.objects.create(
                    selector=selector,
                    elementName=elementName,
                    website_id=site.siteId
                )

                observer = Observer.objects.create(
                    site_id=site.siteId
                )

                elem = TrackedElement.objects.get(website_id=site.pk)
                if site.siteType == "image":
                    take_text = False
                    observeImages = True
                elif site.siteType == "json": # json dont catch the photos
                    take_text = True
                    observeImages = False
                else:
                    take_text = not observeImages

                info = ObserverInfo.objects.create(
                    observer_id=observer.id,
                    info={
                        "id": observer.id,
                        "url": site.siteUrl,
                        "interval": interval,
                        "selector": elem.selector,
                        "take_text": take_text,
                        "observe_images": observeImages ,
                    }
                )

                obs = create_observer(
                    site_type=site.siteType,
                    settings=make_settings_from_info(info.info,site.siteType),
                )
                web_observer.add_observer(obs)
                Observer.objects.filter(id=observer.id).update(hash=obs.get_id())

            return site

        except IntegrityError:
            raise CustomAPIException(
                status_code=400,
                message="Not unique values",
                detail={}
            )
        except Exception as e:
            raise CustomAPIException(
                status_code=500,
                message="Error creating site with observer",
                detail={"error": str(e)}
            )


def _get_site_by_id(data):
    """
    Fetches a tracked website instance based on siteId.
    """
    site_id = data.get('siteId')
    try:
        site = TrackedWebsite.objects.get(siteId=site_id)
        data["site"] = site
        return data
    except TrackedWebsite.DoesNotExist:
        raise serializers.ValidationError("Site do not exists")





class RemoveSiteSerializer(serializers.Serializer):
    """
    Removes the observer and detaches it from the active scheduler.
    """
    siteId = serializers.UUIDField()
    def validate(self, data):
        site = _get_site_by_id(data)
        try:
            obs =Observer.objects.get(site_id=site["site"])
            data["observer"] = obs
            web_observer.remove_observer(obs.hash)
        except Observer.DoesNotExist:
            raise serializers.ValidationError("Observer does not exist")
        return _get_site_by_id(data)

class PatchSiteSerializer(serializers.Serializer):
    """
    Updates site name, description, or tracked element name.
    """
    siteId = serializers.UUIDField()  # need for auth input from param
    siteName = serializers.CharField(required=False,max_length=30)
    siteDescription = serializers.CharField(required=False,max_length=900)
    elementName = serializers.CharField(required=False,max_length=255)
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exists because of checking query params
        siteName = data.get('siteName')
        siteDescription = data.get('siteDescription')
        elementName = data.get('elementName')
        try:
            with transaction.atomic():
                site = TrackedWebsite.objects.get(siteId=site_id)
                data["site"] = site
                if siteName:
                    data["siteName"] = siteName
                if siteDescription:
                    data["siteDescription"] = siteDescription
                if elementName:
                    data["elementName"] = elementName
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")


class ElementIDSerializer(serializers.Serializer):
    """
    Retrieves the ID of the element associated with the given site.
    """
    siteId = serializers.UUIDField()  # need for auth input from param
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exists because of checking query params
        try:
            site = TrackedWebsite.objects.get(siteId=site_id)
            element_id = TrackedElement.get_elemId_by_siteId(site.siteId)
            data["element_id"] = element_id
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")


class RegisterElementChangeSerializer(serializers.ModelSerializer):
    """
     Registers a manual change for a tracked element.
     Also creates a corresponding user update entry.
    """
    element_id = serializers.UUIDField()
    change = serializers.CharField(allow_blank=True,allow_null=True) #can be null
    class Meta:
        model = ElementChange
        fields = [
            "id", "element_id", "change", "detectedAt",
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'detectedAt': {'read_only': True},
        }
    def create(self, validated_data):
        user = self.context['request'].user
        # if element_id is for this user
        element_id = validated_data['element_id']
        site = TrackedElement.objects.get(id=element_id).website
        u_id = UserTrackedWebsites.objects.filter(website_id=site.pk).first().user.id
        if user.id != u_id:
            raise CustomAPIException(status_code=404,message="Do not have access to this",detail={})
        with transaction.atomic():
            elementChange = ElementChange.objects.create(
                element_id=element_id,
                change=validated_data['change'],
            )
            url = TrackedWebsite.objects.get(siteId=site.siteId).siteUrl
            try:
                response = requests.get(url)
                code = response.status_code
            except:
                code = 501
            latesthistory = UserElementUpdate.objects.create(
                user_id=user.id,
                element_id=element_id,
                website_id=site.siteId,
                statusCode=code,
                updateTime = elementChange.detectedAt
            )

        return elementChange


def get_all_updates(id):
    """
    Retrieves the full change/update history for a given website.
    """
    query = '''
    SELECT
        u.updateTime AS update_time,
        ec.textChange AS tchange,
        ec.imageChangeUrl AS urlChange,
        u.statusCode AS status_code,
        u.error as error
    FROM element_changes ec
    JOIN user_element_updates u
    ON u.element_id = ec.element_id
    AND u.updateTime = ec.detectedAt
    WHERE u.website_id = %s 
    ORDER BY u.updateTime DESC'''
    with connection.cursor() as cursor:
        cursor.execute(query, [str(id).replace("-", "")])
        rows = cursor.fetchall()
        entries = [
            {
                "registeredAt": row[0],
                "textChange":row[1],
                "imageChangeUrl":settings.DOMAIN+settings.MEDIA_URL+os.path.basename(row[2]) if row[2] is not None else None,
                "statusCode": row[3] if row[4] is None else -1,
                "error":row[4],
            }
            for row in rows

        ]
        return entries

class SiteDetailSerializer(serializers.Serializer):
    """
     Returns full site details including last update and all changes.
     If `onlyUpdates=true` is passed, only the update list is returned.
    """
    siteId = serializers.UUIDField()  # need for auth input from param
    onlyUpdates = serializers.CharField(required=False,allow_null=True)
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exists because of checking query params
        onlyUpdates = data.get('onlyUpdates')
        try:
            site = TrackedWebsite.objects.get(siteId=site_id)
            if onlyUpdates == "true":
                entries = get_all_updates(site_id)
                data["bare_update_entry"] = entries
            else:
                elem = TrackedElement.objects.get(website_id=site_id)
                last_change = ElementChange.objects.filter(element_id=elem.pk).order_by('-detectedAt').first()
                if last_change:
                    last_change = last_change.detectedAt
                site_details = {
                    "siteInfo":{
                        "siteId":site.siteId,
                        "siteName":site.siteName,
                        "siteUrl":site.siteUrl,
                        "lastUpdateAt":last_change,
                        "selector":elem.selector,
                        "elementName":elem.elementName,
                        "siteType":site.siteType

                    },
                    "updates":get_all_updates(site_id),
                    "trackedSince":site.createdAt,
                    "description":site.siteDescription
                }
                data["site_details"] = site_details
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")


class KLastUpdatesSerializer(serializers.Serializer):
    """
    Fetches the last 10 updates for the authenticated user.
    """
    def validate(self, data):
        user = self.context['request'].user

        updates = list(UserElementUpdate.objects.filter(
            user=user
        ).select_related('website').order_by('-updateTime')[:10])

        updates_data = [{
            "siteId": update.website.pk,
            "siteUrl": update.website.siteUrl,
            "siteName": update.website.siteName,
            "registeredAt": update.updateTime,
            "statusCode": update.statusCode if update.error is None else -1,
            "error": update.error,
        } for update in updates]

        data["updates"] = updates_data
        return data



class SearchSuggestionSerializer(serializers.Serializer):
    """
    Returns up to 10 matching site suggestions for the user based on query string.
    """
    query = serializers.CharField(required=False,allow_null=True)
    def validate(self, data):
        user = self.context['request'].user
        query = data.get("query")
        try:
            items = UserTrackedWebsites.objects.filter(
                user_id=user.pk,
                website__siteName__istartswith = query,
            ).select_related('user','website')[:10]
            items = [{
                "siteId":item.website.pk,
                "siteName":item.website.siteName,
            }for item in items
            ]
            data["items"]=items
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")



#class RemoveObserverSerializer(serializers.Serializer):
#    site_id = serializers.UUIDField()
#    def validate(self, data):
#        data["siteId"] = data["site_id"]
#        site = _get_site_by_id(data)
#        try:
#            obs =Observer.objects.get(site_id=site["site"])
#            data["observer"] = obs
#            web_observer.remove_observer(obs.hash)
#        except Observer.DoesNotExist:
#            raise serializers.ValidationError("Observer does not exist")
#        return data

class GotifyRegisterSerializer(serializers.ModelSerializer):
    """
    Registers or updates Gotify notification configuration for the user.
    """
    url = serializers.CharField(allow_blank=True, allow_null=True, required=False, write_only=True)
    token = serializers.CharField(allow_blank=True, allow_null=True, required=False, write_only=True)

    class Meta:
        model = GotifyInfo
        fields = ["id", "user", "url", "token", "updateTime"]
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'updateTime': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        url = validated_data.get("url")
        token = validated_data.get("token")

        with transaction.atomic():
            gotify, created = GotifyInfo.objects.get_or_create(user=user, defaults={"url": url or "", "token": token or ""})

            if not created:
                updated_fields = []
                if url is not None:
                    gotify.url = url
                    updated_fields.append("url")
                if token is not None:
                    gotify.token = token
                    updated_fields.append("token")
                if updated_fields:
                    gotify.save(update_fields=updated_fields)

        return gotify


class GotifyInfoSerializer(serializers.Serializer):
    """
    Data structure used to return Gotify configuration.
    """
    url = serializers.URLField()
    token = serializers.CharField()


class RemoveGotifySerializer(serializers.Serializer):
    """
    Removes the user's Gotify integration entry.
    """
    def validate(self, data):
        user = self.context['request'].user
        try:
            gotify_entry = GotifyInfo.objects.get(user=user)
            data["gotify"] = gotify_entry
        except GotifyInfo.DoesNotExist:
            raise serializers.ValidationError("Gotify config does not exist for this user")
        return data


class CollectionSerializer(serializers.Serializer):
    """
    Returns a list of all websites tracked by the authenticated user.
    """
    def validate(self, data):
        user = self.context['request'].user
        websites = TrackedWebsite.objects.filter(usertrackedwebsites__user=user)

        websites_data = [{
            "siteId": website.pk,
            "siteName": website.siteName,
        } for website in websites]

        data["websites"] = websites_data
        return data
