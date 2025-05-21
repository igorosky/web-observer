from django.utils import timezone
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import  login,logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .models import UserTrackedWebsites
from .serializers import RegisterSiteSerializer, SiteDetailsSerializer, RemoveSiteSerializer, ElementIDSerializer, \
    PatchSiteSerializer, RegisterElementChangeSerializer
from rest_framework.views import  APIView
from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException

#Server first has to send /get/element-id/siteId=? and if no error then => from this will get element_id, this is needed for response
# from python scraper.
class elementId(APIView):
    """
    GET /element-id/siteId=?
    Response:
    {
     element_id: "uuid" # this is value of PrimaryKey of tracking element
    }
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to get this site",detail={})
        serializer = ElementIDSerializer(data={"siteId":site_id})
        data = validate_or_raise(serializer,status_code=404,message="Search for this site failed")
        elemId = data['element_id']
        return Response({
            "element_id":elemId
        })

class SiteView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        """
         POST /site/
         Request:
         {
         "siteName": "own name of the site",
         "siteUrl": "www.link.com",
         "siteDescription": "good site",
         "elementName":"fancy div"
         "cssSelector":"div.name"
         }
         Response when no errors:
         {
         "siteName":"",
         "siteUrl":"",
         "siteDescription":"",
         }
         Errors:
         405 - bad http method
         400 - errors in input data:
        "message": "",
        "errors": {}

         """
        site = RegisterSiteSerializer(data=request.data,context={'request':request})
        data = validate_or_raise(site,status_code=400,message="Adding page failed")
        site.save() # dont forget when you want change sth in db (especially in creating)!!!
        return Response({
            "siteName": data['siteName'],
            "siteUrl": data['siteUrl'],
            "siteDescription":data['siteDescription'],
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
        data = validate_or_raise(serializer,status_code=404,message="Remove this site failed")
        data['site'].delete()
        return Response(status=204)

#    def get(self,request):
#        """
#           GET /site/?siteId=
#           Request:
#           Response when no errors
#           {
#                "id": ""
#                "name": "",
#                "url": "",
#                "description": "",
#               "created_at": "",
#           }
#           Errors:
#
#          405 - bad http method
#           400 - missing id param:
#           404 - site not found
#           "message": "",
#           "errors": {}
#
#           """
#        site_id = request.query_params.get('siteId')
#        if not site_id:
#            raise CustomAPIException(status_code=400,message="Missing site id",detail={})
#        serializer = SiteDetailsSerializer(data={"siteId":site_id})
#        data = validate_or_raise(serializer,status_code=404,message="Search for this site failed")
#        site = data['site']
#        return Response({
#            "id": str(site.id),
#            "name": site.name,
#            "url": site.url,
#            "description":site.description,
#            "createdAt": site.created_at,
#        })

    def patch(self,request):
        """
           PATCH /site/?siteId=
           Request:
           {
           siteName:""
           siteDescription:"" (OPC)
           }
           Response when no errors 204 HTTP
           Errors:
           405 - bad http method
           400 - missing id param:
           404 - site not found
           "message": "",
           "errors": {}

           """
        site_id = request.query_params.get('siteId')
        if not site_id:
            raise CustomAPIException(status_code=400, message="Missing site id",detail={})
        if not UserTrackedWebsites.exists_site_for_user(site_id,request.user.id):
            raise CustomAPIException(status_code=401,message="Can't permission to patch this site",detail={})
        request.data["siteId"] = site_id
        serializer = PatchSiteSerializer(data=request.data)
        data = validate_or_raise(serializer,status_code=404,message="Patch this site failed")
        site = data["site"]
        site.siteName = data["siteName"]
        site.save(update_fields=['siteName'])
        if "siteDescription" in data:
            site.siteDescription = data["siteDescription"]
            site.save(update_fields=['siteDescription'])
        return Response(status=204)



class TrackingElementChangeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        """
         POST /element/
         Request:
         {
         element_id:"",
         content:"",
         change:"", # required but can be null
         }
         Response when no errors:
         {
         element_id:"",
         content:"",
         change:"",
         }
         Errors:
         405 - bad http method
         400 - errors in input data:
         404 - when somehow user do not have access xto element_id
        "message": "",
        "errors": {}

         """
        elementChange = RegisterElementChangeSerializer(data=request.data,context={'request':request})
        data = validate_or_raise(elementChange,status_code=400,message="Adding change failed")
        elementChange.save() # dont forget when you want change sth in db (especially in creating)!!!
        return Response({
            "element_id": data['element_id'],
            "content": data['content'],
            "change":data['change'],
        })





@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def refresh_site(request):
    ...


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def sites(request):
    ...

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def last_updates(request):
    ...
