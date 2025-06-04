from django.urls import path
from .views import SiteView,elementId,TrackingElementChangeView,LastKUpdatesView,SearchSuggestionView, GotifyView
urlpatterns = [
    path("site/",SiteView.as_view(),name="site_view"),
    path("element/",TrackingElementChangeView.as_view(),name="site_view"),
    path("element-id/",elementId.as_view(),name="element_view"),
    path("updates/",LastKUpdatesView.as_view(),name="last_update_view"),
    path("search/",SearchSuggestionView.as_view(),name="search_view"),
    path("gotify/",GotifyView.as_view(),name="gotify_view"),




]