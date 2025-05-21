import requests
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_unicode_slug
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TrackedWebsite, UserTrackedWebsites, ElementChange, TrackedElement, UserElementUpdate
import uuid
from django.db import transaction
from django_app.utils import validate_or_raise

from django_app.exception_handler import CustomAPIException

User = get_user_model()


class RegisterSiteSerializer(serializers.ModelSerializer):
    cssSelector = serializers.CharField(write_only=True)
    elementName = serializers.CharField(write_only=True)

    class Meta:
        model = TrackedWebsite
        fields = [
            "siteId", "siteName", "siteUrl", "siteDescription", "createdAt",
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

        with transaction.atomic():
            site = TrackedWebsite.objects.create(
                siteName=validated_data['siteName'],
                siteUrl=validated_data['siteUrl'],
                siteDescription=validated_data['siteDescription']
            )
            UserTrackedWebsites.objects.create(
                user_id=user.id,
                website_id=site.siteId
            )
            TrackedElement.objects.create(
                cssSelector=cssSelector,
                elementName=elementName,
                website_id=site.siteId
            )
        return site

def _get_site_by_id(data):
    site_id = data.get('siteId')  # we know that this exsits because of checkign query params
    try:
        site = TrackedWebsite.objects.get(id=site_id)
        data["site"] = site
        return data
    except TrackedWebsite.DoesNotExist:
        raise serializers.ValidationError("Site do not exists")




class SiteDetailsSerializer(serializers.Serializer):
    siteId = serializers.UUIDField() # need for auth inpiut from param
    def validate(self, data):
        return _get_site_by_id(data)


class RemoveSiteSerializer(serializers.Serializer):
    siteId = serializers.UUIDField() # need for auth inpiut from param
    def validate(self, data):
        return _get_site_by_id(data)


class PatchSiteSerializer(serializers.Serializer):
    siteId = serializers.UUIDField()  # need for auth inpiut from param
    siteName = serializers.CharField(required=True,max_length=30)
    siteDescription = serializers.CharField(required=False,max_length=300)

    def validate(self, data):
        site_id = data.get('siteId')  # we know that this exsits because of checkign query params
        siteName = data.get('siteName')
        siteDescription = data.get('siteDescription')
        try:
            site = TrackedWebsite.objects.get(siteId=site_id)
            data["site"] = site
            data["siteName"] = siteName
            if siteDescription:
                data["siteDescription"] = siteDescription
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
        site_id = TrackedElement.objects.get(id=element_id).website
        u_id = UserTrackedWebsites.objects.get(website=site_id).id
        if user.id != u_id:
            raise CustomAPIException(status_code=404,message="Do not have access to this",detail={})
        with transaction.atomic():
            elementChange = ElementChange.objects.create(
                element_id=element_id,
                content=validated_data['content'],
                change=validated_data['change'],
            )
            site_id =  UserTrackedWebsites.get_site_id_user(user.id).website_id
            url = TrackedWebsite.objects.get(siteId=site_id).siteUrl
            try:
                response = requests.get(url)
                code = response.status_code
            except:
                code = 501
            latesthistory = UserElementUpdate.objects.create(
                user_id=user.id,
                element_id=element_id,
                website_id=site_id,
                statusCode=code,
                updateTime = elementChange.detectedAt
            )

        return elementChange