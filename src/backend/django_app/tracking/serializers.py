import requests
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_unicode_slug
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TrackedWebsite, UserTrackedWebsites, ElementChange, TrackedElement, UserElementUpdate, Observer, \
    ObserverInfo
import uuid
from django.db import transaction, connection, IntegrityError
from django_app.utils import validate_or_raise

from django_app.exception_handler import CustomAPIException
from .observers import load_observers_from_db, create_observer, make_settings_from_info
from .observers import  web_observer
User = get_user_model()


class RegisterSiteSerializer(serializers.ModelSerializer):
    elementName = serializers.CharField(write_only=True)
    cssSelector = serializers.CharField(allow_blank=True,allow_null=True,write_only=True)
    jsonSelector = serializers.CharField(allow_blank=True,allow_null=True,write_only=True)
    class Meta:
        model = TrackedWebsite
        fields = [
            "siteId", "siteName", "siteUrl", "siteDescription", "createdAt","type","jsonSelector",
            "cssSelector", "elementName"
        ]
        extra_kwargs = {
            'siteId': {'read_only': True},
            'createdAt': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user

        cssSelector = validated_data.pop('cssSelector')
        elementName = validated_data.pop('elementName')
        jsonSelector = validated_data.pop('jsonSelector')

        with transaction.atomic():
            site = TrackedWebsite.objects.create(
                siteName=validated_data['siteName'],
                siteUrl=validated_data['siteUrl'],
                siteDescription=validated_data['siteDescription'],
                type=validated_data['type']
            )
            UserTrackedWebsites.objects.create(
                user_id=user.id,
                website_id=site.siteId
            )
            TrackedElement.objects.create(
                cssSelector=cssSelector,
                jsonSelector=jsonSelector,
                elementName=elementName,
                website_id=site.siteId
            )
        return site

def _get_site_by_id(data):
    site_id = data.get('siteId')  # we know that this exsits because of checkign query params
    try:
        site = TrackedWebsite.objects.get(siteId=site_id)
        data["site"] = site
        return data
    except TrackedWebsite.DoesNotExist:
        raise serializers.ValidationError("Site do not exists")





class RemoveSiteSerializer(serializers.Serializer):
    siteId = serializers.UUIDField() # need for auth inpiut from param
    def validate(self, data):
        return _get_site_by_id(data)


class PatchSiteSerializer(serializers.Serializer):
    siteId = serializers.UUIDField()  # need for auth inpiut from param
    siteName = serializers.CharField(required=False,max_length=30)
    siteDescription = serializers.CharField(required=False,max_length=900)
    elementName = serializers.CharField(required=False,max_length=255)
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exsits because of checkign query params
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
    siteId = serializers.UUIDField()  # need for auth inpiut from param
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exsits because of checkign query params
        try:
            site = TrackedWebsite.objects.get(siteId=site_id)
            element_id = TrackedElement.get_elemId_by_siteId(site.siteId)
            data["element_id"] = element_id
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")


class RegisterElementChangeSerializer(serializers.ModelSerializer):
    element_id = serializers.UUIDField()
    change = serializers.CharField(allow_blank=True,allow_null=True) #can be null
    class Meta:
        model = ElementChange
        fields = [
            "id", "element_id", "content", "change", "detectedAt",
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
                content=validated_data['content'],
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
    WHERE u.website_id = %s '''
    with connection.cursor() as cursor:
        cursor.execute(query, [str(id).replace("-", "")])
        rows = cursor.fetchall()
        entries = [
            {
                "registeredAt": row[0],
                "textChange":row[1],
                "imageChangeUrl":row[2],
                "statusCode": row[3],
                "error":row[4]
            }
            for row in rows
        ]
        return entries

class SiteDetailSerializer(serializers.Serializer):
    siteId = serializers.UUIDField()  # need for auth inpiut from param
    onlyUpdates = serializers.CharField(required=False,allow_null=True)
    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exsits because of checkign query params
        onlyUpdates = data.get('onlyUpdates')
        try:
            site = TrackedWebsite.objects.get(siteId=site_id)
            if onlyUpdates == "true":
                entries = get_all_updates(site_id)
                data["bare_update_entry"] = entries
            else:
                elem = TrackedElement.objects.get(website_id=site_id)
                last_change = ElementChange.objects.filter(element_id=elem.pk).order_by('-id').first()
                if last_change:
                    last_change = last_change.detectedAt
                site_details = {
                    "siteInfo":{
                        "siteId":site.siteId,
                        "siteName":site.siteName,
                        "siteUrl":site.siteUrl,
                        "lastUpdatedAt":last_change,
                        "cssSelector":elem.cssSelector,
                        "elementName":elem.elementName
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
    def validate(self, data):
        user = self.context['request'].user
        try:
            updates = UserElementUpdate.objects.filter(
                user_id=user.id
            ).select_related('website').order_by('-id')[:10]
            updates = [{
                "siteId":update.website.pk,
                "siteUrl":update.website.siteUrl,
                "siteName":update.website.siteName,
                "registeredAt":update.website.createdAt,
                "statusCode":update.statusCode,
                "error":update.error,
            }for update in updates
            ]
            data["updates"]=updates
            return data
        except TrackedWebsite.DoesNotExist:
            raise serializers.ValidationError("Site do not exists")


class SearchSuggestionSerializer(serializers.Serializer):
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



class RegisterObserverSerializer(serializers.ModelSerializer):
    site_id = serializers.UUIDField()
    interval = serializers.CharField(write_only=True)
    take_text = serializers.CharField(write_only=True)
    observe_images = serializers.CharField(write_only=True)
    class Meta:
        model = Observer
        fields = ["id","site_id","interval","take_text","observe_images"]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        try:
            with transaction.atomic():
                observer = Observer.objects.create(
                    site_id=validated_data['site_id']
                )
                site = TrackedWebsite.objects.get(siteId=validated_data['site_id'])
                elem = TrackedElement.objects.get(website_id=site.pk)
                info = ObserverInfo.objects.create(
                    observer_id = observer.id,
                    info = {
                        "id" : observer.id,
                        "url": site.siteUrl,
                        "interval": validated_data['interval'],
                        "css_selector": elem.cssSelector,
                        "json_selector": elem.jsonSelector, # in loading and creating if and after that to list steps...
                        "take_text": False if site.type =="image" else validated_data['take_text'],
                        "observe_images": validated_data['observe_images'],
                    }
                )

                # we have to start here observers
                obs = create_observer(site_type=site.type,settings=make_settings_from_info(info.info))
                web_observer.add_observer(obs)
                Observer.objects.filter(id=observer.id).update(hash=obs.get_id())

            return observer
        except IntegrityError:
            raise  CustomAPIException(status_code=400,message="Not unique values",detail={})
        except TrackedWebsite.DoesNotExist:
            raise  CustomAPIException(status_code=404,message="Site do not exists",detail={})




class RemoveObserverSerializer(serializers.Serializer):
    site_id = serializers.UUIDField()
    def validate(self, data):
        data["siteId"] = data["site_id"]
        site = _get_site_by_id(data)
        try:
            obs =Observer.objects.get(site_id=site["site"])
            data["observer"] = obs
            web_observer.remove_observer(obs.hash)
        except Observer.DoesNotExist:
            raise serializers.ValidationError("Observer does not exist")
        return data

