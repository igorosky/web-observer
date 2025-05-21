from django.urls import path
from . import views
from .views import SiteView,elementId,TrackingElementChangeView
urlpatterns = [
    path("site/",SiteView.as_view(),name="site_view"),
    path("element/",TrackingElementChangeView.as_view(),name="site_view"),
    path("element-id/",elementId.as_view(),name="element_view"),
   # path("register-site/", RegisterSiteView.as_view(), name="register_site"),
   # path("site-details/", SiteDetailsView.as_view(), name="site_detail"),
   # path("refresh-site/", views.refresh_site, name="refresh_site"),
   # path("update-site-details/",UpdateSiteView.as_view() , name="update_site_details"),
    path("sites/", views.sites, name="sites"),
    path("last-updates/", views.last_updates, name="last_updates"),
    #path("remove-site/", RemoveSiteView.as_view(), name="remove_site"),

]