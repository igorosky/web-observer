from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException
from django_app.custom_session import CustomSessionAuthentication
from django_app.custom_authentication import CustomIsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserTrackedWebsites, TrackedElement, GotifyInfo
from .serializers import (
    RegisterSiteWithObserverSerializer,
    RemoveSiteSerializer,
    ElementIDSerializer,
    PatchSiteSerializer,
    RegisterElementChangeSerializer,
    SiteDetailSerializer,
    KLastUpdatesSerializer,
    SearchSuggestionSerializer,
    GotifyRegisterSerializer,
    RemoveGotifySerializer,
    GotifyInfoSerializer,
    CollectionSerializer,
)


class elementId(APIView):
    """
    GET /element-id/siteId=?
    Get element ID
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id", detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id, request.user.id):
            raise CustomAPIException(status_code=401, message="Can't permission to get this site", detail={})
        serializer = ElementIDSerializer(data={"siteId": site_id})
        serializer = validate_or_raise(serializer, status_code=404, message="Search for this site failed")
        elemId = serializer.validated_data['element_id']
        return Response({"element_id": elemId})


class TrackingElementChangeView(APIView):
    """
    POST /element/
    Register element change
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = RegisterElementChangeSerializer(data=request.data, context={'request': request})
        serializer = validate_or_raise(serializer, status_code=400, message="Adding change failed")
        serializer.save()
        return Response({
            "element_id": serializer.validated_data['element_id'],
            "change": serializer.validated_data['change'],
        })


class SiteView(APIView):
    """
    POST /site/
    DELETE /site/?siteId=
    GET /site/?siteId=&onlyUpdates=[true/false/undefined]
    PATCH /site/?siteId=
    Manage tracked site
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = RegisterSiteWithObserverSerializer(data=request.data, context={'request': request})
        serializer = validate_or_raise(serializer, status_code=400, message="Adding page failed")
        serializer.save()
        return Response({
            "siteId": serializer.data["siteId"],
            "siteName": serializer.validated_data['siteName'],
            "siteUrl": serializer.validated_data['siteUrl'],
            "siteDescription": serializer.validated_data['siteDescription'],
            "siteType": serializer.validated_data['siteType']
        })

    def delete(self, request):
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id", detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id, request.user.id):
            raise CustomAPIException(status_code=401, message="Can't permission to delete this site", detail={})
        serializer = RemoveSiteSerializer(data={"siteId": site_id})
        serializer = validate_or_raise(serializer, status_code=404, message="Remove this site failed")
        serializer.validated_data['site'].delete()
        return Response(status=204)

    def get(self, request):
        onlyUpdates = request.query_params.get('onlyUpdates')
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id", detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id, request.user.id):
            raise CustomAPIException(status_code=401, message="Can't permission to get this site", detail={})
        serializer = SiteDetailSerializer(data={"siteId": site_id, "onlyUpdates": onlyUpdates})
        serializer = validate_or_raise(serializer, status_code=404, message="Get site info failed")
        if onlyUpdates == "true":
            site = serializer.validated_data['bare_update_entry']
        else:
            site = serializer.validated_data['site_details']
        return Response(site)

    def patch(self, request):
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id", detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id, request.user.id):
            raise CustomAPIException(status_code=401, message="Can't permission to patch this site", detail={})
        data = request.data.copy()
        data["siteId"] = site_id
        serializer = PatchSiteSerializer(data=data)
        serializer = validate_or_raise(serializer, status_code=404, message="Patch this site failed")
        site = serializer.validated_data["site"]
        if "siteName" in serializer.validated_data:
            site.siteName = serializer.validated_data["siteName"]
            site.save(update_fields=['siteName'])
        if "siteDescription" in serializer.validated_data:
            site.siteDescription = serializer.validated_data["siteDescription"]
            site.save(update_fields=['siteDescription'])
        if "elementName" in serializer.validated_data:
            element = TrackedElement.objects.get(website_id=site_id)
            element.elementName = serializer.validated_data["elementName"]
            element.save(update_fields=['elementName'])
        return Response(status=204)


class LastKUpdatesView(APIView):
    """
    GET /updates/
    Get last updates
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        serializer = KLastUpdatesSerializer(data={}, context={'request': request})
        serializer = validate_or_raise(serializer, status_code=400, message="Get last updates failed")
        updates = serializer.validated_data["updates"]
        return Response(updates)


class SearchSuggestionView(APIView):
    """
    GET /search/?q=
    Get search suggestions
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q")
        serializer = SearchSuggestionSerializer(data={"query": query}, context={'request': request})
        serializer = validate_or_raise(serializer, status_code=400, message="Search failed")
        suggestion = serializer.validated_data["items"]
        return Response(suggestion)


class GotifyView(APIView):
    """
    PUT /gotify/
    GET /gotify/
    DELETE /gotify/
    Manage Gotify settings
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def put(self, request):
        url = request.data.get('url')
        token = request.data.get('token')
        if url is None and token is None:
            raise CustomAPIException(status_code=400, message="Missing params", detail={})
        serializer = GotifyRegisterSerializer(data={"url": url, "token": token}, context={"request": request})
        serializer = validate_or_raise(serializer, status_code=400, message="Gotify update failed")
        serializer.save()
        return Response(status=200)

    def get(self, request):
        try:
            gotify = GotifyInfo.objects.get(user=request.user)
        except GotifyInfo.DoesNotExist:
            raise CustomAPIException(status_code=404, message="Gotify config not found", detail={})
        serializer = GotifyInfoSerializer({
            "url": gotify.url,
            "token": gotify.token
        })
        return Response(serializer.data, status=200)

    def delete(self, request):
        serializer = RemoveGotifySerializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        gotify = serializer.validated_data["gotify"]
        gotify.delete()
        return Response(status=204)


class CollectionView(APIView):
    """
    GET /collection/
    Get all sites
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        serializer = CollectionSerializer(data={}, context={'request': request})
        serializer = validate_or_raise(serializer, status_code=400, message="Get last updates failed")
        webs = serializer.validated_data["websites"]
        return Response(webs)
