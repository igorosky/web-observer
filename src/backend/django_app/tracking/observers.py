from observing.web_observer_options import WebObserverOptions
from observing.html_observer import HtmlObserver
from observing.image_observer import ImageObserver
from observing.json_observer import JsonObserver

from observing.web_observer_scheduler import WebObserverScheduler

from .models import UserTrackedWebsites, TrackedElement, ObserverInfo, Observer, TrackedWebsite

# importing state of observers
# run the observer state


def make_settings_from_info(info,site_type):
    return {
        "id": int(info["id"]),
        "url": str(info["url"]),
        "interval": int(info.get("interval", 30)),
        "css_selector": info.get("selector"),
        "take_text": bool(info.get("take_text", False)),
        "observe_images": bool(info.get("observe_images", False)),
        "steps_to_get_element": [
            WebObserverOptions.StepToGetElement(element_id=info["selector"])
        ] if site_type == "json" else []
    }


def create_observer(site_type,settings):
    from .change_api import register_change
    if site_type == "html":
        obs = HtmlObserver(WebObserverOptions(**settings), notify=lambda notification: register_change(notification),path_to_images="imgs")
    if site_type == "json":
        obs = JsonObserver(WebObserverOptions(**settings), notify=lambda notification: register_change(notification))
    if site_type == "image":
        obs = ImageObserver(WebObserverOptions(**settings), notify=lambda notification: register_change(notification),path_to_images="imgs")
    return obs


def load_observers_from_db():
    obs_lst = []
    observers_with_elements = ObserverInfo.objects.select_related(
        'observer__site'
    ).prefetch_related(
        'observer__site__trackedelement_set'
    ).all()

    for observer_info in observers_with_elements:
        site = observer_info.observer.site
        site_type = site.type
        elements = site.trackedelement_set.all()
        for elem in elements:
            settings = make_settings_from_info(observer_info.info,site_type)
            obs = create_observer(site_type,settings)
            Observer.objects.filter(id=observer_info.info['id']).update(hash=obs.get_id())
            obs_lst.append(obs)
    return obs_lst






#singleton
web_observer = WebObserverScheduler(cores=10)

def load_observers():
    observers = load_observers_from_db()
    for obs in observers:
        web_observer.add_observer(obs)


