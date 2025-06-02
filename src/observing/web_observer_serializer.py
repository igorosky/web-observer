from .image_observer import ImageObserver
from .html_observer import HtmlObserver
from .web_observer_options import WebObserverOptions
from .web_observer import WebObserver
from typing import Any
import json

def WebObserverToJson(web_observer: WebObserver | WebObserverOptions) -> str:
  def serializer_helper(obj):
    ans: dict[str, Any] = obj.__dict__
    if not isinstance(obj, WebObserver):
      ans.pop('notify', None)  # Remove notify function from serialization
      ans.pop('last_response_code', None)  # Remove last_response_code from serialization
      ans.pop('id', None)  # Remove id from serialization
      if isinstance(obj, HtmlObserver) or isinstance(obj, ImageObserver):
        ans.pop('current_digest', None)  # Remove current_digest from serialization
        ans.pop('path_to_images', None)  # Remove path_to_images from serialization
    return ans
  return json.dumps(web_observer, default=serializer_helper)


def JsonToWebObserver(json_str: str) -> WebObserver:
  def deserialization_helper(d: dict[str, Any]) -> WebObserver | WebObserverOptions:
    if 'type' not in d:
      if 'id' in d:
        return WebObserverOptions(**d)
      else:
        return WebObserverOptions.StepToGetElement(**d)
    if d['type'] == 'html':
      return HtmlObserver(**d)
  return json.loads(json_str, object_hook=deserialization_helper)
