from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException
from django_app.custom_session import CustomSessionAuthentication
from django_app.custom_authentication import CustomIsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import  authentication_classes, permission_classes

from .models import UserTrackedWebsites, TrackedElement, GotifyInfo
from .serializers import RegisterSiteWithObserverSerializer, RemoveSiteSerializer, ElementIDSerializer, \
    PatchSiteSerializer, RegisterElementChangeSerializer, SiteDetailSerializer, KLastUpdatesSerializer, \
    SearchSuggestionSerializer, GotifyRegisterSerializer, \
    RemoveGotifySerializer, GotifyInfoSerializer, CollectionSerializer
from rest_framework.views import  APIView

#TO DELETE
class elementId(APIView):
    """
    GET /element-id/siteId=?
    Response:
    {
     element_id: "uuid" # this is value of PrimaryKey of tracking element
    }
    """
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def get(self,request):
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to get this site",detail={})
        serializer = ElementIDSerializer(data={"siteId":site_id})
        serializer = validate_or_raise(serializer,status_code=404,message="Search for this site failed")
        elemId = serializer.validated_data['element_id']
        return Response({
            "element_id":elemId
        })

#TO DELETE (dont works)
class TrackingElementChangeView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def post(self,request):
        """
         POST /element/
         Request:
         {
         element_id:"",
         content:"",
         change:"", # required but can be null
         """
        serializer = RegisterElementChangeSerializer(data=request.data,context={'request':request})
        serializer = validate_or_raise(serializer,status_code=400,message="Adding change failed")
        serializer.save() # dont forget when you want change sth in db (especially in creating)!!!
        return Response({
            "element_id": serializer.validated_data['element_id'],
            "change":serializer.validated_data['change'],
        })



class SiteView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def post(self,request):
        """
         POST /site/
         Request:
         {
         "siteName": "own name of the site",
         "siteUrl": "www.link.com",
         "siteDescription": "good site",
         "elementName":"fancy div"
         "selector" " " !!! selector
         "type":{html,json,image}
         "interval" " " textbox for client
         "observe_images" :true -> only false -> text

         }
         Response when no errors:
         {
         "siteId":" "
         "siteName":"",
         "siteUrl":"",
         "siteDescription":"",
         "type: " "
         "observer_id":""
         }
         Errors:
         405 - bad http method
         400 - errors in input data:
        "message": "",
        "errors": {}
         """
        serializer = RegisterSiteWithObserverSerializer(data=request.data,context={'request':request})
        serializer = validate_or_raise(serializer,status_code=400,message="Adding page failed")
        serializer.save()
        return Response({
            "siteId":serializer.data["siteId"],
            "siteName": serializer.validated_data['siteName'],
            "siteUrl": serializer.validated_data['siteUrl'],
            "siteDescription":serializer.validated_data['siteDescription'],
            "siteType":serializer.validated_data['siteType']
            #observer_id
        })


    def delete(self,request):
        """
           DELETE /site/?siteId=
           Request:
           Response when no errors: 204 HTTP
           Errors:
           405 - bad http method
           400 - missing id param:
           401 - deleted not your site
           404 - site not found
           "message": "",
           "errors": {}
           """
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to delete this site",detail={})
        serializer = RemoveSiteSerializer(data={"siteId": site_id})
        serializer = validate_or_raise(serializer,status_code=404,message="Remove this site failed")
        serializer.validated_data['site'].delete()
        return Response(status=204)

    def get(self,request):
        """
           GET /site/?siteId=&onlyUpdates=[true/false/undefined]
           Request:
           Response when no errors (too big to be here but in short: onlyUp=True => Only updates else updates with
           whole descriptions, a lots of strings)
           Errors:

           405 - bad http method
           400 - missing id param:
           404 - site not found
           "message": "",
           "errors": {}

           """
        onlyUpdates = request.query_params.get('onlyUpdates')
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to get this site",detail={})
        serializer = SiteDetailSerializer(data={"siteId": site_id,"onlyUpdates":onlyUpdates})
        serializer = validate_or_raise(serializer,status_code=404,message="Get site info failed")
        if onlyUpdates == "true":
            site = serializer.validated_data['bare_update_entry']
        else:
            site = serializer.validated_data['site_details']
        return Response(site)

    def patch(self,request):
        """
           PATCH /site/?siteId=
           Request:
           {
           siteName:"" (OPC)
           siteDescription:"" (OPC)
           "elementName": (OPC)
           }
           Response when no errors 204 HTTP
           Errors:
           405 - bad http method
           400 - missing id param:
           401 - patch not your site
           404 - site not found
           "message": "",
           "errors": {}

           """
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to patch this site",detail={})
        data = request.data.copy()  # Tworzy modyfikowalną kopię
        data["siteId"] = site_id
        serializer = PatchSiteSerializer(data=data)
        serializer = validate_or_raise(serializer,status_code=404,message="Patch this site failed")
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
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def get(self,request):
        """
           GET /updates/
           Response when no errors 200 list of k-last updates:
                [{
                "siteId":" ",
                "siteUrl":" ",
                "siteName":" ",
                "registeredAt":" ",
                "statusCode":" "
                "error: "
                }]
           Errors:
           405 - bad http method
           404 - site not found
           "message": "",
           "errors": {}

           """
        serializer = KLastUpdatesSerializer(data={},context={'request':request})
        serializer = validate_or_raise(serializer,status_code=400,message="Get last updates failed")
        updates = serializer.validated_data["updates"]
        return Response(updates)

class SearchSuggestionView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def get(self,request):
        """
           q - text we're typing
           GET /search/?q=
           Response when no errors 200
            [{
            siteId:" ",
            siteName:" "
            }]
           Errors:
           405 - bad http method
           404 - site not found
           "message": "",
           "errors": {}

           """
        query = request.query_params.get("q")
        serializer = SearchSuggestionSerializer(data={"query":query},context={'request':request})
        serializer = validate_or_raise(serializer,status_code=400,message="Search failed")
        suggestion = serializer.validated_data["items"]
        return Response(suggestion)



class GotifyView(APIView):
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
        """
        DELETE /gotify/
        Odpowiedzi:
        204 – sukces
        404 – brak wpisu dla użytkownika
        """
        serializer = RemoveGotifySerializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)

        gotify = serializer.validated_data["gotify"]
        gotify.delete()

        return Response(status=204)


class CollectionView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]

    def get(self,request):
        serializer = CollectionSerializer(data={},context={'request':request})
        serializer = validate_or_raise(serializer,status_code=400,message="Get last updates failed")
        webs = serializer.validated_data["websites"]
        return Response(webs)

